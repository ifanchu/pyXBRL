# pyXBRL

This moduls is to read in an XBRL xml file, parse it and then calculate predefined common financial facts and financial measurements for analytical use.

This module was inspired by [lukeroisak's pysec module](https://github.com/lukerosiak/pysec)

## Library Dependencies

[python 2.7.8](https://www.python.org/download/releases/2.7.8/)

[lxml](http://lxml.de/)

## Usage

The main class is **XBRL** class in xbrl.py, the constructor takes a path to the XBRL xml documents desired to parse. The path can be either local full filepath of a valid url to the xml

```python
>>> url = 'http://www.sec.gov/Archives/edgar/data/320193/000119312514277160/aapl-20140628.xml'
>>> x = xbrl.XBRL(url)
```

After constructing the object, you will have following information at your disposal

### x.dei: A map that maps from xbrl.DEI object to its value
DEI stands for Document and Entity Information which is a section in each financial report containing basic info for the filing entity and the report itself.

DEI is a enum-like object which means we have defined several DEI objects in the class and you can see them by using

```python
>>> DEI.all()
(<DEI: EntityCurrentReportingStatus>, <DEI: EntityCentralIndexKey>, <DEI: CurrentFiscalYearEndDate>, <DEI: DocumentPeriodEndDate>, <DEI: DocumentFiscalPeriodFocus>, <DEI: EntityWellKnownSeasonedIssuer>, <DEI: EntityVoluntaryFilers>, <DEI: TradingSymbol>, <DEI: DocumentFiscalYearFocus>, <DEI: DocumentType>, <DEI: EntityFilerCategory>, <DEI: AmendmentFlag>, <DEI: EntityRegistrantName>, <DEI: EntityCommonStockSharesOutstanding>, <DEI: EntityPublicFloat>)
```

which will return a list of DEI objects that was pre-defined.
You can of course add any DEI object you want to fetch from the report. Note that when defining your own DEI, add it to the DEI class and the name must match the dei tag announced by SEC.

The DEI tags stars with "dei:"

To get any DEI value from x, use

```python
>>> x.dei[DEI.TradingSymbol]
AAPL
```

### x.common_facts: A map which maps from CommonFact objects to its value

**common_fact.CommonFact** class is a class to represent a financial fact commonly used in accounting. For example, CommonFact.Assets is defined for total assets reported in Balance Sheet.

CommonFact class, like DEI, is an enum-like class which we pre-defined around 50 common facts for different financial statements.

To list all predefined CommonFact objects:
```python
>>> CommonFact.all()
```

### x.common_measurements: A map which maps from CommonMeasurements to its value

**common_measurement.CommonMeasurement** class is a class to represent a financial measurement, which is often calculated from CommonFact, but could also be calculated from other CommonMeasurement

To list all predefined CommonMeasurement objects
```python
>>> CommonMeasurement.all()
```

## usgaap_concept.py

This module provides 2 classes: `UsGaapConcept` and `UsGaapConceptPool`. These 2 clases are to provide access to the standard US GAAP financial reporting Taxonomy established by [FASB](http://www.fasb.org/home). You can get all valid us-gaap tag from these classes.

Note that there are nearly 18000 entries of UsGaapConcept, so reading the pickle could take about 2 seconds.

## How to add additional CommonFact

To add additional CommonFact, open `common_fact.py`, and you will see a lot of CommonFact have been defined. You just need to identify the concepts to be used in your CommonFact and defined your own entry at the end of the module.

For example, let's assume you want to add a CommonFact named MyFact and the value should be fetched from us-gaap tag us-gaap:FinancialGuaranteeInsuranceSegmentMember, and if this value is not found in the XBRL xml file, try to compute it by this equation (CommonFact.CommonStockSharesIssued - CommonFact.DepreciationDepletionAndAmortization), your new CommonFact entry will look like:

```
CommonFact.MyFact = CommonFact(
    'MyFact',
    (
        'us-gaap:FinancialGuaranteeInsuranceSegmentMember',
    ),
    (
        ('CommonStockSharesIssued', 'DepreciationDepletionAndAmortization', '-'),
    )
)
```

## How to add additional CommonMeasurement

A measurement is a value calculated from several CommonFact or CommonMeasurement values.

Open `common_measurement.py` and you will see a lot of measurements have been defined. To add your own measurement, follow the instruction provided in the module.

Take Market Capitalization as an example, this entry is defined as

```
CommonMeasurement.MarketCapitalization = CommonMeasurement(
    'MarketCapitalization',
    'Market Cap',
    'Market Capitalization equals to common shares outstaning times stock price',
    ('Quote', CommonFact.CommonStockSharesIssued, '*'),
)
```

The first argument is the name of the measurement which needs to be identical to the string as CommonMeasurement.**MarketCapitalization**.

The second argument is the abbreviation for this measurement, if any.

The third argument is the definition for this measurement, if any.

The fourth argument is the core of measurement computation: the equation. Each measurement takes a tuple in [Reverse Polish Notation](http://en.wikipedia.org/wiki/Reverse_Polish_notation) as its calculation equation.

The equation tuple takes 4 kinds of objects: CommonFact, CommonMeasurement, a char in '+-*/', and Quote.

The most confusing part here is Quote. Because some of the measurements require stock price to calculate the value, for example, P/E Ratio is defined as stock price divided by EPS. However, there is no stock price data in the XBRL xml file. So we have to get this data from external.

That's where `quote_helper.py` comes into play, `quote_helper.py` defines a single method
```get_quote(symbol, fiscal_period_end_date):```
which should return a float as a representative value of stock price for the given symbol on the given date.

Once this method is functional, `CommonMeasurement.calculate` method will get the value from this method and compute based on the equation.
