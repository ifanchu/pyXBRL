import rpn_helper

class CommonFact(object):
    """
    This class is to represent a common fact in Accounting, for example, Current Assets. In a single XBRL report(or an Annual Financial Report), a common fact can either be fetched by looking up a us-gaap tag or imputed by several other us-gaap tags.
    As a result, this class takes an argument of possible fact names which is a tuple of possible us-gaap tags which this common fact can be fetched from.
    As well as an argument impute_equations, which is a tuple of tuple represents a series of possible equations to impute the value for this common fact. The equation is using Reverse Polish Notation
    For example, a CommonFact named 'Assets' represents the total amount of Assets in this statement, its possible_fact_name could be 'Assets', 'Asset', and etc.
    """
    # pool is a set of strings contains all object names, for convenient retrieval
    pool = {}

    def __init__(self,
                 name,
                 possible_fact_names,
                 impute_equations=None):
        """
        Args:
            name CommonFact name
            possible_fact_names A tuple of strings which are valid us-gaap tags
            impute_equations A tuple of tuples which lists all possible calculations for this CommonFact calculated from other CommonFact. Use Reverse Polish Notation. This calculation will only be calculated if the value is not present in the xbrl xml file.
        """
        if name and isinstance(name, str):
            self.name = name
            self.possible_fact_names = possible_fact_names
            self.impute_equations = impute_equations
            self.pool[name] = self
        else:
            raise ValueError('Given name is not a string')

    def impute(self, common_facts):
        """
        Given a map maps from CommonFact to its value, return imputed value based on the impute equation if this CommonFact has no value in the first place
        """
        if common_facts[self] != float(0):
            return common_facts[self]
        ret = float(0)
        if not self.impute_equations:
            return ret
        for equation in self.impute_equations:
            equation = list(equation)
            equation = [self.pool[x] if x in self.pool else x for x in equation]
            equation = [common_facts[x] if x in common_facts else x for x in equation]
            ret = rpn_helper.calculate(equation)
            if ret:
                break
        return ret

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.name)

    def __getattr__(self, name):
        lookup = name
        if lookup in self.__dict__:
            return self.__dict__[lookup]
        return self.__dict__[name] if name in self.__dict__ else None

    @classmethod
    def all(cls):
        """
        Returns a tuple which contains all members
        """
        return tuple(cls.pool.values())

############################################################
###             Balance Sheet
############################################################
# Total Current Assets
CommonFact.CurrentAssets = CommonFact(
    'CurrentAssets',
    (
        'us-gaap:AssetsCurrent',
    ),
)
# Inventory
CommonFact.InventoryNet = CommonFact(
    'InventoryNet',
    (
        'us-gaap:InventoryNet',
    ),
)
# Total noncurrent assets
CommonFact.NoncurrentAssets = CommonFact(
    'NoncurrentAssets',
    (
        'us-gaap:AssetsNoncurrent',
    ),
    (
        ('Assets', 'CurrentAssets', '-'),
    ),
)

CommonFact.PropertyPlantAndEquipmentNet = CommonFact(
    'PropertyPlantAndEquipmentNet',
    (
        'us-gaap:PropertyPlantAndEquipmentNet',
    ),
)

# Retained earnings
CommonFact.RetainedEarningsAccumulatedDeficit = CommonFact(
    'RetainedEarningsAccumulatedDeficit',
    (
        'us-gaap:RetainedEarningsAccumulatedDeficit',
    ),
)

# Cash and cash equivalents
CommonFact.CashAndCashEquivalentsAtCarryingValue = CommonFact(
    'CashAndCashEquivalentsAtCarryingValue',
    (
        'us-gaap:CashAndCashEquivalentsAtCarryingValue',
    ),
)

# Net intangible assets
CommonFact.IntangibleAssetsNetExcludingGoodwill = CommonFact(
    'IntangibleAssetsNetExcludingGoodwill',
    (
        'us-gaap:IntangibleAssetsNetExcludingGoodwill',
    ),
)

# Goodwill
CommonFact.Goodwill = CommonFact(
    'Goodwill',
    (
        'us-gaap:Goodwill',
    ),
)
# Total Assets
CommonFact.Assets = CommonFact(
    'Assets',
    (
        'us-gaap:Assets',
    ),
)


# CurrentLiabilities
CommonFact.CurrentLiabilities = CommonFact(
    'CurrentLiabilities',
    (
        'us-gaap:LiabilitiesCurrent',
    ),
)

# NoncurrentLiabilities
CommonFact.NoncurrentLiabilities = CommonFact(
    'NoncurrentLiabilities',
    (
        'us-gaap:LiabilitiesNoncurrent',
        'us-gaap:EquityMethodInvestmentSummarizedFinancialInformationNoncurrentLiabilities',
    ),
    (
        ('Liabilities', 'CurrentLiabilities', '-'),
        ('CurrentLiabilities',),
    ),
)

# Liabilities
CommonFact.Liabilities = CommonFact(
    'Liabilities',
    (
        'us-gaap:Liabilities',
    ),
    (
        ('LiabilitiesAndEquity', 'CommitmentsAndContingencies', '-', 'TemporaryEquity', '+', 'Equity', '+'),
    ),
)

# LiabilitiesAndEquity: Total liabilities and stockholders' equity
CommonFact.LiabilitiesAndEquity = CommonFact(
    'LiabilitiesAndEquity',
    (
        'us-gaap:LiabilitiesAndStockholdersEquity',
        'us-gaap:LiabilitiesAndPartnersCapital',
        'us-gaap:Assets',
    ),
)


# CommitmentsAndContingencies
CommonFact.CommitmentsAndContingencies = CommonFact(
    'CommitmentsAndContingencies',
    (
        'us-gaap:CommitmentsAndContingencies',
    ),
)

# TemporaryEquity
CommonFact.TemporaryEquity = CommonFact(
    'TemporaryEquity',
    (
        'us-gaap:TemporaryEquityRedemptionValue',
        'us-gaap:RedeemablePreferredStockCarryingAmount',
        'us-gaap:TemporaryEquityCarryingAmount',
        'us-gaap:TemporaryEquityValueExcludingAdditionalPaidInCapital',
        'us-gaap:TemporaryEquityCarryingAmountAttributableToParent',
        'us-gaap:RedeemableNoncontrollingInterestEquityFairValue',
    ),
)

# RedeemableNoncontrollingInterest
CommonFact.RedeemableNoncontrollingInterest = CommonFact(
    'RedeemableNoncontrollingInterest',
    (
        'us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount',
        'us-gaap:RedeemableNoncontrollingInterestEquityCommonCarryingAmount',
    ),
)

# EquityAttributableToNoncontrollingInterest
CommonFact.EquityAttributableToNoncontrollingInterest = CommonFact(
    'EquityAttributableToNoncontrollingInterest',
    (
        'us-gaap:MinorityInterest',
        'us-gaap:PartnersCapitalAttributableToNoncontrollingInterest',
    ),
)

# EquityAttributableToParent
CommonFact.EquityAttributableToParent = CommonFact(
    'EquityAttributableToParent',
    (
        'us-gaap:StockholdersEquity',
        'us-gaap:LiabilitiesAndPartnersCapital',
    ),
    (
        ('Equity', 'EquityAttributableToNoncontrollingInterest', '-'),
        ('Equity',),
    ),
)

# Equity: Total stockholders' Equity
CommonFact.Equity = CommonFact(
    'Equity',
    (
        'us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
        'us-gaap:StockholdersEquity',
        'us-gaap:PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest',
        'us-gaap:PartnersCapital',
        'us-gaap:CommonStockholdersEquity',
        'us-gaap:MemberEquity',
        'us-gaap:AssetsNet',
        'us-gaap:EquityAttributableToParent',
    ),
    (
        ('EquityAttributableToParent', 'EquityAttributableToNoncontrollingInterest', '+',),
    ),
)
CommonFact.AccountsReceivable = CommonFact(
    'AccountsReceivable',
    (
        'us-gaap:AccountsReceivableNetCurrent',
    ),
)

############################################################
###             Income Statements
############################################################
# Revenues
CommonFact.Revenues = CommonFact(
    'Revenues',
    (
        'us-gaap:Revenues',
        'us-gaap:SalesRevenueNet',
        'us-gaap:SalesRevenueServicesNet',
        'us-gaap:RevenuesNetOfInterestExpense',
        'us-gaap:RegulatedAndUnregulatedOperatingRevenue',
        'us-gaap:HealthCareOrganizationRevenue',
        'us-gaap:InterestAndDividendIncomeOperating',
        'us-gaap:RealEstateRevenueNet',
        'us-gaap:RevenueMineralSales',
        'us-gaap:OilAndGasRevenue',
        'us-gaap:FinancialServicesRevenue',
        'us-gaap:RegulatedAndUnregulatedOperatingRevenue',
    ),
    (
        ('GrossProfit', 'CostOfRevenue', '+'),
    ),
)

# CostOfRevenue
CommonFact.CostOfRevenue = CommonFact(
    'CostOfRevenue',
    (
        'us-gaap:CostOfRevenue',
        'us-gaap:CostOfServices',
        'us-gaap:CostOfGoodsSold',
        'us-gaap:CostOfGoodsAndServicesSold',
    ),
    (
        ('GrossProfit', 'Revenues', '+'),
        ('CostsAndExpenses', 'OperatingExpenses', '-'),
    ),
)

# CostsAndExpenses: Total costs and expenses
CommonFact.CostsAndExpenses = CommonFact(
    'CostsAndExpenses',
    (
        'us-gaap:CostsAndExpenses',
    ),
    (
        ('CostOfRevenue', 'OperatingExpenses', '+'),
        ('Revenues', 'OperatingIncomeLoss', '-', 'OtherOperatingIncome', '-'),
    ),
)

# OpeartingIncomeLoss
CommonFact.OperatingIncomeLoss = CommonFact(
    'OperatingIncomeLoss',
    (
        'us-gaap:OperatingIncomeLoss',
    ),
    (
        ('OperatingIncomeLoss', 'IncomeFromEquityMethodInvestments', '-'),
        ('IncomeBeforeEquityMethodInvestments', 'NonoperatingIncomeLoss', '+', 'InterestAndDebtExpense', '-'),
    ),
)

# GrossProfit
CommonFact.GrossProfit = CommonFact(
    'GrossProfit',
    (
        'us-gaap:GrossProfit',
    ),
    (
        ('Revenues', 'CostOfRevenue', '-'),
    ),
)

# OperatingExpenses
CommonFact.OperatingExpenses = CommonFact(
    'OperatingExpenses',
    (
        'us-gaap:OperatingExpenses',
        'us-gaap:OperatingCostsAndExpenses',
    ),
    (
        ('CostsAndExpenses', 'CostOfRevenue', '-'),
    ),
)

# OtherOperatingIncome
CommonFact.OtherOperatingIncome = CommonFact(
    'OtherOperatingIncome',
    (
        'us-gaap:OtherOperatingIncome',
    ),
    (
        ('OperatingIncomeLoss', 'GrossProfit', '-', 'OperatingExpenses', '-'),
    ),
)

# NonoperatingIncomeLoss
CommonFact.NonoperatingIncomeLoss = CommonFact(
    'NonoperatingIncomeLoss',
    (
        'us-gaap:NonoperatingIncomeExpense',
        'us-gaap:NonoperatingIncomeExpense',
    )
)

# InterestAndDebtExpense
CommonFact.InterestAndDebtExpense = CommonFact(
    'InterestAndDebtExpense',
    (
        'us-gaap:InterestAndDebtExpense',
    ),
    (
        ('IncomeBeforeEquityMethodInvestments', 'OperatingIncomeLoss', '-', 'NonoperatingIncomeLoss', '+'),
    ),
)

# IncomeBeforeEquityMethodInvestments: income before income taxes
CommonFact.IncomeBeforeEquityMethodInvestments = CommonFact(
    'IncomeBeforeEquityMethodInvestments',
    (
        'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',
    ),
    (
        ('IncomeFromContinuingOperationsBeforeTax', 'IncomeFromEquityMethodInvestments', '-'),
    ),
)

# IncomeFromEquityMethodInvestments
CommonFact.IncomeFromEquityMethodInvestments = CommonFact(
    'IncomeFromEquityMethodInvestments',
    (
        'us-gaap:IncomeLossFromEquityMethodInvestments',
    )
)

# IncomeFromContinuingOperationsBeforeTax
CommonFact.IncomeFromContinuingOperationsBeforeTax = CommonFact(
    'IncomeFromContinuingOperationsBeforeTax',
    (
        'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
    ),
    (
        ('IncomeBeforeEquityMethodInvestments', 'IncomeFromEquityMethodInvestments', '+'),
        ('IncomeFromContinuingOperationsAfterTax', 'IncomeTaxExpenseBenefit', '+'),
    ),
)

# IncomeTaxExpenseBenefit
CommonFact.IncomeTaxExpenseBenefit = CommonFact(
    'IncomeTaxExpenseBenefit',
    (
        'us-gaap:IncomeTaxExpenseBenefit',
        'us-gaap:IncomeTaxExpenseBenefitContinuingOperations',
    )
)

# IncomeFromContinuingOperationsAfterTax
CommonFact.IncomeFromContinuingOperationsAfterTax = CommonFact(
    'IncomeFromContinuingOperationsAfterTax',
    (
        'us-gaap:IncomeLossBeforeExtraordinaryItemsAndCumulativeEffectOfChangeInAccountingPrinciple',
    ),
    (
        ('NetIncomeLoss', 'IncomeFromDiscontinuedOperations', '-', 'ExtraordaryItemsGainLoss', '-'),
        ('IncomeFromContinuingOperationsBeforeTax', 'IncomeTaxExpenseBenefit', '-'),
    ),
)

# IncomeFromDiscontinuedOperations
CommonFact.IncomeFromDiscontinuedOperations = CommonFact(
    'IncomeFromDiscontinuedOperations',
    (
        'us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTax',
        'us-gaap:DiscontinuedOperationGainLossOnDisposalOfDiscontinuedOperationNetOfTax',
        'us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity',
    )
)

# ExtraordaryItemsGainLoss
CommonFact.ExtraordaryItemsGainLoss = CommonFact(
    'ExtraordaryItemsGainLoss',
    (
        'us-gaap:ExtraordinaryItemNetOfTax',
    )
)

# NetIncomeLoss: net income
CommonFact.NetIncomeLoss = CommonFact(
    'NetIncomeLoss',
    (
        'us-gaap:ProfitLoss',
        'us-gaap:NetIncomeLoss',
        'us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic',
        'us-gaap:IncomeLossFromContinuingOperations',
        'us-gaap:IncomeLossAttributableToParent',
        'us-gaap:IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest',
    )
)

# NetIncomeAvailableToCommonStockholdersBasic
CommonFact.NetIncomeAvailableToCommonStockholdersBasic = CommonFact(
    'NetIncomeAvailableToCommonStockholdersBasic',
    (
        'us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic',
    ),
    (
        ('NetIncomeAttributableToParent',),
    ),
)

# PreferredStockDividendsAndOtherAdjustments
CommonFact.PreferredStockDividendsAndOtherAdjustments = CommonFact(
    'PreferredStockDividendsAndOtherAdjustments',
    (
        'us-gaap:PreferredStockDividendsAndOtherAdjustments',
    ),
    (
        ('NetIncomeAttributableToParent', 'NetIncomeAvailableToCommonStockholdersBasic', '-'),
    ),
)

# NetIncomeAttributableToNoncontrollingInterest
CommonFact.NetIncomeAttributableToNoncontrollingInterest = CommonFact(
    'NetIncomeAttributableToNoncontrollingInterest',
    (
        'us-gaap:NetIncomeLossAttributableToNoncontrollingInterest',
    )
)

# NetIncomeAttributableToParent
CommonFact.NetIncomeAttributableToParent = CommonFact(
    'NetIncomeAttributableToParent',
    (
        'us-gaap:NetIncomeLoss',
    )
)

# OtherComprehensiveIncome
CommonFact.OtherComprehensiveIncome = CommonFact(
    'OtherComprehensiveIncome',
    (
        'us-gaap:OtherComprehensiveIncomeLossNetOfTax',
    ),
    (
        ('ComprehensiveIncome', 'NetIncomeLoss', '-'),
    ),
)

# ComprehensiveIncome
CommonFact.ComprehensiveIncome = CommonFact(
    'ComprehensiveIncome',
    (
        'us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest',
        'us-gaap:ComprehensiveIncomeNetOfTax',
    ),
    (
        ('NetIncomeLoss', ),
    ),
)

# ComprehensiveIncomeAttributableToParent
CommonFact.ComprehensiveIncomeAttributableToParent = CommonFact(
    'ComprehensiveIncomeAttributableToParent',
    (
        'us-gaap:ComprehensiveIncomeNetOfTax',
    ),
    (
        ('ComprehensiveIncome',),
    ),
)

# ComprehensiveIncomeAttributableToNoncontrollingInterest
CommonFact.ComprehensiveIncomeAttributableToNoncontrollingInterest = CommonFact(
    'ComprehensiveIncomeAttributableToNoncontrollingInterest',
    (
        'us-gaap:ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest',
    )
)

#Impute: NonoperatingIncomeLossPlusInterestAndDebtExpense
CommonFact.NonoperatingIncomeLossPlusInterestAndDebtExpense = CommonFact(
    'NonoperatingIncomeLossPlusInterestAndDebtExpense',
    (),
    (
        ('NonoperatingIncomeLoss', 'InterestAndDebtExpense', '+'),
    ),
)

############################################################
###             Statements of Cash Flows
############################################################

# NetCashFlow
CommonFact.NetCashFlow = CommonFact(
    'NetCashFlow',
    (
        'us-gaap:CashAndCashEquivalentsPeriodIncreaseDecrease',
        'us-gaap:CashPeriodIncreaseDecrease',
        'us-gaap:NetCashProvidedByUsedInContinuingOperations',
    ),
    (
        ('NetCashFlowsOperating', 'NetCashFlowsInvesting', '+', 'NetCashFlowsFinancing', '+'),
    ),
)

# NetCashFlowsOperating: Net cash provided by operating activities
CommonFact.NetCashFlowsOperating = CommonFact(
    'NetCashFlowsOperating',
    (
        'us-gaap:NetCashProvidedByUsedInOperatingActivities',
    ),
    (
        ('NetCashFlowsOperatingContinuing',),
    ),
)

# NetCashFlowsInvesting
CommonFact.NetCashFlowsInvesting = CommonFact(
    'NetCashFlowsInvesting',
    (
        'us-gaap:NetCashProvidedByUsedInInvestingActivities',
    ),
    (
        ('NetCashFlowsInvestingContinuing',),
    ),
)

# NetCashFlowsFinancing
CommonFact.NetCashFlowsFinancing = CommonFact(
    'NetCashFlowsFinancing',
    (
        'us-gaap:NetCashProvidedByUsedInFinancingActivities',
    ),
    (
        ('NetCashFlowsFinancingContinuing',),
    ),
)

# NetCashFlowsOperatingContinuing
CommonFact.NetCashFlowsOperatingContinuing = CommonFact(
    'NetCashFlowsOperatingContinuing',
    (
        'us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
    ),
    (
        ('NetCashFlowsOperating', 'NetCashFlowsOperatingDiscontinued', '-'),
        ('NetCashFlowsInvesting', 'NetCashFlowsInvestingDiscontinued', '-'),
        ('NetCashFlowsFinancing', 'NetCashFlowsFinancingDiscontinued', '-'),
    ),
)

# NetCashFlowsInvestingContinuing
CommonFact.NetCashFlowsInvestingContinuing = CommonFact(
    'NetCashFlowsInvestingContinuing',
    (
        'us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
        'us-gaap:NetCashProvidedByUsedInInvestingActivities',
    )
)

# NetCashFlowsFinancingContinuing
CommonFact.NetCashFlowsFinancingContinuing = CommonFact(
    'NetCashFlowsFinancingContinuing',
    (
        'us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations',
        'us-gaap:NetCashProvidedByUsedInFinancingActivities',
    )
)

# NetCashFlowsOperatingDiscontinued
CommonFact.NetCashFlowsOperatingDiscontinued = CommonFact(
    'NetCashFlowsOperatingDiscontinued',
    (
        'us-gaap:CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations',
    )
)

# NetCashFlowsInvestingDiscontinued
CommonFact.NetCashFlowsInvestingDiscontinued = CommonFact(
    'NetCashFlowsInvestingDiscontinued',
    (
        'us-gaap:CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations',
    )
)

# NetCashFlowsFinancingDiscontinued
CommonFact.NetCashFlowsFinancingDiscontinued = CommonFact(
    'NetCashFlowsFinancingDiscontinued',
    (
        'us-gaap:CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations',
    )
)

# NetCashFlowsDiscontinued
CommonFact.NetCashFlowsDiscontinued = CommonFact(
    'NetCashFlowsDiscontinued',
    (
        'us-gaap:NetCashProvidedByUsedInDiscontinuedOperations',
    ),
    (
        ('NetCashFlowsOperatingDiscontinued', 'NetCashFlowsInvestingDiscontinued', '+', 'NetCashFlowsFinancingDiscontinued', '+'),
    ),
)

# ExchangeGainsLosses
CommonFact.ExchangeGainsLosses = CommonFact(
    'ExchangeGainsLosses',
    (
        'us-gaap:EffectOfExchangeRateOnCashAndCashEquivalents',
        'us-gaap:EffectOfExchangeRateOnCashAndCashEquivalentsContinuingOperations',
        'us-gaap:CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations',
    )
)

CommonFact.NetCashFlowsContinuing = CommonFact(
    'NetCashFlowsContinuing',
    (),
    (
        ('NetCashFlowsOperatingContinuing', 'NetCashFlowsInvestingContinuing', '+', 'NetCashFlowsFinancingContinuing', '+'),
    ),
)

####################
### Statements of Operations
####################
CommonFact.EarningsPerShareBasic = CommonFact(
    'EarningsPerShareBasic',
    (
        'us-gaap:EarningsPerShareBasic',
    ),
)

CommonFact.EarningsPerShareDiluted = CommonFact(
    'EarningsPerShareDiluted',
    (
        'us-gaap:EarningsPerShareDiluted',
    ),
)
# shares used to calculate EarningsPerShareBasic
CommonFact.WeightedAverageNumberOfSharesOutstandingBasic = CommonFact(
    'WeightedAverageNumberOfSharesOutstandingBasic',
    (
        'us-gaap:WeightedAverageNumberOfSharesOutstandingBasic',
    ),
)
# shares used to calculate EarningsPerShareDiluted
CommonFact.WeightedAverageNumberOfDilutedSharesOutstanding = CommonFact(
    'WeightedAverageNumberOfDilutedSharesOutstanding',
    (
        'us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding',
    ),
)

CommonFact.CommonStockDividendsPerShareDeclared = CommonFact(
    'CommonStockDividendsPerShareDeclared',
    (
        'us-gaap:CommonStockDividendsPerShareDeclared',
    ),
)

CommonFact.CommonStockSharesIssued = CommonFact(
    'CommonStockSharesIssued',
    (
        'us-gaap:CommonStockSharesIssued',
    ),
)
CommonFact.DepreciationDepletionAndAmortization = CommonFact(
    'DepreciationDepletionAndAmortization',
    (
        'us-gaap:DepreciationDepletionAndAmortization',
        'us-gaap:DepreciationAmortizationAndAccretionNet',
    ),
)

if __name__ == '__main__':
    print CommonFact.all()
