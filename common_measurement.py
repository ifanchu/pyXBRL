from common_fact import CommonFact
import rpn_helper

class CommonMeasurement(object):
    """
    A CommonMeasurement is a calculated number from some facts that can indicate the performance of a stock.
    For example, ROE (Return on Equity) is the amount of net income returned as a percentage of shareholders equity.
    This class provides basic implementation and a set of predefined measurement for your disposal.
    """

    pool = {}

    def __init__(self,
                 name,
                 abbr,
                 definition,
                 equation):
        """
        Args:
            name Measurement name
            abbr Measurement abbreviation
            definition Measurement definition
            equation A tuple of strings which indicates how to calculate this measurement using CommonFact, based on Reverse Polish Notation. Each item in this tuple could be
                1. CommonFact or CommonMeasurement object
                2. '+', '-', '/', '*'
        """
        if not equation or not name:
            raise ValueError('name and equation are required')
        self.name = name
        self.abbreviation = abbr if abbr else self.name
        self.definition = definition
        self.equation = equation
        self.pool[name] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.name)

    def calculate(self, common_facts, common_measurements, quote=1):
        """
        Given common_facts as a map which maps from CommonFact to its value and common_measurements which maps from CommonMeasurement to its value, calculate the measurement value based on the equation using Reverse Polish Notation.
        The reason to have 2 maps here is:
            1. common_facts, most of the measurements are calculated using CommonFact, for example, WorkingCapital = CurrentAssets - CurrentLiabilities
            2. common_measurements, some of the measurements are calculated using CommonMeasurement as well
        Return a float
        """
        if not common_facts or len(common_facts) == 0:
            raise ValueError('Given common_facts is either None or nothing in it')
        ret = float(0)
        if not self.equation:
            return ret
        copy = list(self.equation)
        copy = [common_facts[f] if (isinstance(f, CommonFact) and f in common_facts) else f for f in copy]
        copy = [common_measurements[f] if (isinstance(f, CommonMeasurement) and f in common_measurements) else f for f in copy]
        copy = [quote if (isinstance(f, str) and f == 'Quote') else f for f in copy]
        copy = [0 if (isinstance(f, str) and f not in '+-*/') else f for f in copy]
        # if there is still CommonFact or CommonMeasurement object in copy array, then it means that is a CommonMeasurement and it has not yet been calculated, so put it as 0
        copy = [0 if (isinstance(f, CommonFact) or isinstance(f, CommonMeasurement)) else f for f in copy]
        # for index in xrange(len(copy)):
        #     value = copy[index]
        #     if isinstance(value, float) or isinstance(value, int):
        #         continue
        #     if isinstance(value, str) and value in '+-*/':
        #         continue
        #     if value in common_measurements:
        #         copy[index] = common_measurements[value]
        #     else:
        #         copy[index] = 0
        try:
            ret = rpn_helper.calculate(copy)
        except ZeroDivisionError:
            return 0
        return ret

    @classmethod
    def all(cls):
        """
        Returns a tuple which contains all members
        """
        return tuple(cls.pool.values())

############################################################
###             Balance Sheet
############################################################
CommonMeasurement.WorkingCapital = CommonMeasurement(
    'WorkingCapital',
    'WorkingCapital',
    'The working capital ratio (Current Assets/Current Liabilities) indicates whether a company has enough short term assets to cover its short term debt. Anything below 1 indicates negative W/C (working capital). While anything over 2 means that the company is not investing excess assets. Most believe that a ratio between 1.2 and 2.0 is sufficient',
    (CommonFact.CurrentAssets, CommonFact.CurrentLiabilities, '-'),
)
CommonMeasurement.CurrentRatio = CommonMeasurement(
    'CurrentRatio',
    'CurrentRatio',
    "A liquidity ratio that measures a company's ability to pay short-term obligations.",
    (CommonFact.CurrentAssets, CommonFact.CurrentLiabilities, '/'),
)
CommonMeasurement.QuickAssets = CommonMeasurement(
    'QuickAssets',
    'QuickAssets',
    '',
    (CommonFact.CurrentAssets, CommonFact.InventoryNet, '-'),
)
CommonMeasurement.QuickAssetRatio = CommonMeasurement(
    'QuickAssetRatio',
    'QuickAssetRatio',
    '',
    (CommonMeasurement.QuickAssets, CommonFact.CurrentLiabilities, '/'),
)
CommonMeasurement.NetQuickAssets = CommonMeasurement(
    'NetQuickAssets',
    'NetQuickAssets',
    '',
    (CommonMeasurement.QuickAssets, CommonFact.CurrentLiabilities, '-'),
)
CommonMeasurement.DebtToEquityRatio = CommonMeasurement(
    'DebtToEquityRatio',
    'DebtToEquityRatio',
    '',
    (CommonFact.Liabilities, CommonFact.Equity, '/'),
)
############################################################
###             Income Statements
############################################################
CommonMeasurement.OperatingMargin = CommonMeasurement(
    'OperatingMargin',
    'OperatingMargin',
    '',
    (CommonFact.OperatingIncomeLoss, CommonFact.Revenues, '/'),
)
CommonMeasurement.GrossMarginPercentage = CommonMeasurement(
    'GrossMarginPercentage',
    'GrossMarginPercentage',
    '',
    (CommonFact.GrossProfit, CommonFact.Revenues, '/'),
)
CommonMeasurement.NetProfitRatio = CommonMeasurement(
    'NetProfitRatio',
    'NetProfitRatio',
    '',
    (CommonFact.NetIncomeLoss, CommonFact.Revenues, '/'),
)
# P/E Ratio is calculated as Stock Market Price / EPS
# market price is not included in financial report, EPS is
# requires quote data, need to compute this during import
CommonMeasurement.PriceEarningsRatio = CommonMeasurement(
    'PriceEarningsRatio',
    'P/E Ratio',
    "A valuation ratio of a company's current share price compared to its per-share earnings.",
    ('Quote', CommonFact.EarningsPerShareBasic, '/'),
)

CommonMeasurement.ROA = CommonMeasurement(
    'ROA',
    'ROA',
    'Return on Assets',
    (CommonFact.NetIncomeLoss, CommonFact.Assets, '/'),
)
CommonMeasurement.ROE = CommonMeasurement(
    'ROE',
    'ROE',
    'Return on Equity',
    (CommonFact.NetIncomeLoss, CommonFact.Equity, '/'),
)
CommonMeasurement.ROR = CommonMeasurement(
    'ROR',
    'ROR',
    'Return on Revenues',
    (CommonFact.NetIncomeLoss, CommonFact.Revenues, '/'),
)
CommonMeasurement.FreeCashFlow = CommonMeasurement(
    'FreeCashFlow',
    'FCF',
    'Free Cash Flow',
    (CommonFact.NetCashFlowsOperatingContinuing, CommonFact.NetCashFlowsInvestingContinuing, '-'),
)
# PriceToFreeCashFlowRatio requires quote data, need to compute this during import
CommonMeasurement.MarketCapitalization = CommonMeasurement(
    'MarketCapitalization',
    'Market Cap',
    'Market Capitalization equals to common shares outstaning times stock price',
    ('Quote', CommonFact.CommonStockSharesIssued, '*'),
)
CommonMeasurement.PriceToFreeCashFlowRatio = CommonMeasurement(
    'PriceToFreeCashFlowRatio',
    'Price to FCF',
    'Price to Free Cash Flow',
    (CommonMeasurement.MarketCapitalization, CommonMeasurement.FreeCashFlow, '/'),
)
