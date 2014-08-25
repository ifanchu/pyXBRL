from lxml import etree
from common_fact import CommonFact
from common_measurement import CommonMeasurement
from datetime import date
from quote_helper import get_quote

class Context(object):
    """ A simulated Enum class to represent 2 different contexts: Instant and Duration
    """
    Duration, Instant = range(2)

class DEI(object):
    """
    DEI stands for Document and Entity Information. For each XBRL report, there will be a section for DEI, and this class is to provide easy access to those commonly-defined DEI attributes.
    """
    # pool is a set of strings contains all object names, for convenient retrieval
    pool = set()

    def __init__(self, name):
        if name and isinstance(name, str):
            self.name = name
            self.pool.add(name)
            self.fact_name = 'dei:{0}'.format(self.name)
        else:
            raise ValueError('Given name is not a string')

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
        return tuple([cls.__dict__[d] for d in cls.pool])

DEI.AmendmentFlag = DEI('AmendmentFlag')
DEI.CurrentFiscalYearEndDate = DEI('CurrentFiscalYearEndDate')
DEI.DocumentFiscalPeriodFocus = DEI('DocumentFiscalPeriodFocus')
DEI.DocumentFiscalYearFocus = DEI('DocumentFiscalYearFocus')
DEI.DocumentPeriodEndDate = DEI('DocumentPeriodEndDate')
DEI.DocumentType = DEI('DocumentType')
DEI.EntityCentralIndexKey = DEI('EntityCentralIndexKey')
DEI.EntityCommonStockSharesOutstanding = DEI('EntityCommonStockSharesOutstanding')
DEI.EntityCurrentReportingStatus = DEI('EntityCurrentReportingStatus')
DEI.EntityFilerCategory = DEI('EntityFilerCategory')
DEI.EntityPublicFloat = DEI('EntityPublicFloat')
DEI.EntityRegistrantName = DEI('EntityRegistrantName')
DEI.EntityVoluntaryFilers = DEI('EntityVoluntaryFilers')
DEI.EntityWellKnownSeasonedIssuer = DEI('EntityWellKnownSeasonedIssuer')
DEI.TradingSymbol = DEI('TradingSymbol')


class XBRL(object):
    """
    This class represents an xbrl xml file from SEC EDGAR.
    For example: http://www.sec.gov/Archives/edgar/data/320193/000119312513416534/aapl-20130928.xml
    """

    def __init__(self, url):
        """
        This url can be a local file path or a http url points to the xml file
        """
        self.url = url
        try:
            self.doc_root = etree.parse(url).getroot()
        except IOError as err:
            raise err
        self.nsmap = {}
        for key in self.doc_root.nsmap.keys():
            if key:
                self.nsmap[key] = self.doc_root.nsmap[key]
        self.nsmap['xbrli'] = 'http://www.xbrl.org/2003/instance'
        self.nsmap['xlmns'] = 'http://www.xbrl.org/2003/instance'

        # The year this report was filed, DEI.DocumentFiscalYearFocus
        self.fiscal_year = 0
        # The date of the fiscal period ends for this report, DEI.DocumentPeriodEndDate
        self.fiscal_period_end_date = None

        # A map that maps from DEI objects to its value
        self.dei = {}
        self._determine_dei()

        # find instant and duration contextRef
        self.context_instant = ''
        self.context_duration = ''
        self._find_contexts()

        # A map that maps from FinancialCommonFact objects to its value
        self.common_facts = {}
        self._determine_common_facts()

        # A map that maps from FinancialMeasurement objects to its value
        self.common_measurements = {}
        self._calculate_measurements()

    def _determine_common_facts(self):
        """
        Based on this XBRL xml document, try to fetch or determine the values for all CommonFact and store it in self.common_facts
        """
        # fetch
        for fact in CommonFact.all():
            value = float(0)
            if not fact.possible_fact_names:
                self.common_facts[fact] = value
                continue
            for candidate in fact.possible_fact_names:
                # get_fact_value returns string
                temp = self.get_fact_value(candidate)
                if temp and len(temp) > 0:
                    try:
                        value = float(temp)
                        # this break here means that we take the first valid value from possible_fact_names
                        break
                    except ValueError:
                        pass
            self.common_facts[fact] = value
        for fact in self.common_facts.keys():
            value = self.common_facts[fact]
            if value == float(0):
                try:
                    value = fact.impute(self.common_facts)
                except Exception as err:
                    print 'Imputation failed: {0}, equaltion: {1} on xbrl {2} because {3}'.format(fact, fact.impute_equations, self.url, err)
                self.common_facts[fact] = value

    def get_empty_common_facts(self):
        """
        Return a generator generates CommonFact object which was not found in this XBRL xml
        """
        for fact, value in self.common_facts.items():
            if value == float(0):
                yield (fact, value)

    def get_determined_common_facts(self):
        """
        Return a generator for the facts that have been fetched, imputed and determined which have a value for it
        """
        for fact, value in self.common_facts.items():
            if value != float(0):
                yield (fact, value)

    def _calculate_measurements(self):
        """
        Calculate CommonMeasurement and put the result in self.common_measurements
        """
        quote_month_avg = get_quote(self.dei[DEI.TradingSymbol], self.fiscal_period_end_date)
        for m in CommonMeasurement.all():
            # measurement calculation could use both facts and measurements, so supply both
            value = m.calculate(self.common_facts, self.common_measurements, quote_month_avg)
            self.common_measurements[m] = value
        for m, value in self.common_measurements.items():
            if value == 0:
                value = m.calculate(self.common_facts, self.common_measurements, quote_month_avg)
                self.common_measurements[m] = value

    def _find_contexts(self):
        """
        Each XBRL xml contains a lot of different contexts, could represent different dimensions. We only need 2 from them, one is the context for instant and one for duration.
        This search process is based on the observation that
            1. For each <context>, it contains 2 children: entity and period
            2. For current instant and duration context, entity has only 1 child whose tag is "<identifier>"
            3. For current instant context, there is only 1 child "<instant>" under "<period>", and its value is equal to <dei:DocumentPeriodEndDate>
            4. For current duration context, there are 2 children "<startDate>" and "<endDate>" under "<period>", and the value for "<endDate>" is equal to <dei:DocumentPeriodEndDate>
        """
        context_instant = ''
        context_duration = ''
        # get END_DATE, which is also the date in file name
        # we can not use self.dei[DEI.dei_DocumentPeriodEndDate] because right now self.dei has not yet been initialized
        END_DATE = str(self.fiscal_period_end_date)
        document_type = self.dei[DEI.DocumentType]
        # get all nodes for <context id=??>
        for node in self.doc_root.xpath("//*[local-name() = 'context']"):
            # as we are not sure about the return order, we need to determine the 2 nodes by its tag
            entity_node = None
            period_node = None
            for child in node.getchildren():
                # _Element.tag contains full xmlns prefix, so need to take substring
                tag = child.tag[child.tag.find('}')+1:]
                if tag == 'entity':
                    # entity node
                    entity_node = child
                elif tag == 'period':
                    # period node
                    period_node = child
            # children under entity must be 1
            if len(entity_node.getchildren()) != 1:
                continue
            # the one child under entity must have tag 'identifier'
            if not 'identifier' in entity_node.getchildren()[0].tag:
                continue
            if len(period_node.getchildren()) == 1:
                # candidate for instant
                instant_node = period_node.getchildren()[0]
                if instant_node.text != END_DATE:
                    continue
                context_instant = node.get('id')
            elif len(period_node.getchildren()) == 2:
                # candidate for duration
                start_date_node = period_node.getchildren()[0]
                end_date_node = period_node.getchildren()[1]
                if end_date_node.text != END_DATE:
                    continue
                # determine startDate
                if 'Q' in document_type:
                    # A quarter report, there could have been multiple same endDate, so we need to check on start date, which will be 3 moths earlier than endDate
                    year, month = self.fiscal_period_end_date.year, self.fiscal_period_end_date.month
                    start_month = 12 if (month - 2) % 12 == 0 else (month - 2) % 12
                    start_year = year - 1 if month <= 2 else year
                    filter_text1 = '{0}-{1:02d}'.format(start_year, start_month)
                    # some company put start date to the last day of previous month, so we need to check both
                    start_month = 12 if (month - 3) % 12 == 0 else (month - 3) % 12
                    start_year = year - 1 if month <= 3 else year
                    filter_text2 = '{0}-{1:02d}'.format(start_year, start_month)
                    # print filter_text1, filter_text2
                    if filter_text1 not in start_date_node.text and filter_text2 not in start_date_node.text:
                        continue
                context_duration = node.get('id')
        self.context_instant = context_instant
        self.context_duration = context_duration

    def _determine_dei(self):
        """
        For all DEI, fetch the value from XBRL xml and put it in self.dei
        """
        for dei in DEI.all():
            fact_name = dei.fact_name
            # value = self.get_fact_value(fact_name)
            nodes = self.doc_root.xpath('//{0}'.format(fact_name), namespaces=self.nsmap)
            value = nodes[0].text if nodes and len(nodes) > 0 else ''
            if not value:
                value = ''
            self.dei[dei] = value
        if not self.dei[DEI.TradingSymbol] or self.dei[DEI.TradingSymbol] == '':
            self.dei[DEI.TradingSymbol] = self.url.split('/')[-1].split('.')[0].split('-')[0].upper()
        tokens = self.dei[DEI.DocumentPeriodEndDate].split('-')
        tokens = tuple(int(x) for x in tokens)
        self.fiscal_period_end_date = date(tokens[0], tokens[1], tokens[2])
        # DEI.DocumentFiscalYearFocus could be absent, fetch it from DEI.DocumentPeriodEndDate
        if not self.dei[DEI.DocumentFiscalYearFocus]:
            self.dei[DEI.DocumentFiscalYearFocus] = self.fiscal_period_end_date.year
        # determine self.fiscal_year and self.fiscal_period_end_date
        self.fiscal_year = int(self.dei[DEI.DocumentFiscalYearFocus])

    def _get_elementlist(self, fact_name, context=Context.Duration):
        """
        In an XBRL xml document, there will be multiple context defined, but only 1 instant context and 1 duration context for current year.
        The logic here is that if context was specified, then we set that context as main, and another one as secondary. We first get the nodes for main context, and if there is no nodes returned, we add the nodes for secondary context.

        Returns a tuple of lxml.etree._Element
        """
        ret = []
        if context == Context.Duration:
            main, secondary = self.context_duration, self.context_instant
        elif context == Context.Instant:
            main, secondary = self.context_instant, self.context_duration
        ret.extend(self.doc_root.xpath("//{0}[@contextRef='{1}']".format(fact_name, main), namespaces=self.nsmap))
        if len(ret) == 0:
            ret.extend(self.doc_root.xpath("//{0}[@contextRef='{1}']".format(fact_name, secondary), namespaces=self.nsmap))
        return tuple(ret)

    def get_fact_value(self, fact_name):
        """
        Given fact_name and filter_text, return the text for that fact. If not found, return empty string
        """
        ret = self._get_elementlist(fact_name)
        return ret[0].text if ret else ''

    def get_common_fact(self, common_fact):
        """
        A conenience method to get the common fact value from self.common_facts
        """
        if not isinstance(common_fact, CommonFact):
            raise ValueError('Given common_fact is not of type CommonFact')
        if common_fact not in self.common_facts:
            return ''
        return self.common_facts[common_fact]
