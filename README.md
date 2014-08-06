# py-sec-xbrl

This simple API is to read in an XBRL xml file, parse it and then calculate common financial facts and financial measurements for analytical use.

This API was inspired from [lukeroisak's pysec module](https://github.com/lukerosiak/pysec)

## Library Dependencies

[python 2.7.8](https://www.python.org/download/releases/2.7.8/)
[lxml](http://lxml.de/)

## Usage

The main class is **XBRL** class in xbrl.py, the constructor takes a path to the XBRL xml documents desired to parse. The path can be either local full filepath of a valid url to the xml

```python
>>> url = 'http://www.sec.gov/Archives/edgar/data/320193/000119312514277160/aapl-20140628.xml'
>>> x = xbrl.XBRL(url)
```

After constructing the object, you will have following information for your desposal

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
