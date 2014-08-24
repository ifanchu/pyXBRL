"""
This class is to represent the us-gaap concepts.
The concepts.csv was modified from the xlsx file, the "UGT *.xlsx" file was downloaded from fasb.org: http://www.fasb.org/cs/ContentServer?c=Page&pagename=FASB%2FPage%2FSectionPage&cid=1176160582432
Take the first sheet "Concept" from the xlsx.
Remove all columns after deprecatedLabel.
Remove all rows except for dei and us-gaap
"""
import os
import pickle
import json

class UsGaapConcept(object):
    """
    This class represents one line in concepts.csv
    """
    def __init__(self,
                 _prefix,
                 _name,
                 _type,
                 _enumerations,
                 _substitutionGroup,
                 _balance,
                 _periodType,
                 _abstract,
                 _label,
                 _documentation,
                 _deprecatedLabel):
        if not _prefix or not _name:
            raise ValueError('_prefix and _name can not be None or empty')
        self.prefix = _prefix
        self.name = _name
        self.type = _type
        self.enumerations = _enumerations
        self.substitutionGroup = _substitutionGroup
        self.balance = _balance
        self.periodType = _periodType
        self.abstract = True if _abstract else False
        self.label = _label
        self.documentation = _documentation
        self.deprecated = True if _deprecatedLabel else False

        self.tag = '{0}:{1}'.format(self.prefix, self.name)

    @classmethod
    def create_instance(cls, tokens):
        """
        Given a tuple of list, each token maps to init parameter
        """
        tokens = tuple([x.replace('"', '') for x in tokens])
        if len(tokens) != 11:
            return None
        try:
            o = UsGaapConcept(tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7], tokens[8], tokens[9], tokens[10])
        except ValueError:
            return None
        return o

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.tag == other.tag

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.tag)

    def json(self):
        return json.dumps(self)

class UsGaapConceptPool(object):
    """
    This class represents the entire collection of UsGaapConcept, provide convenience method to retrieve all concepts and access to specific concept.
    """

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    PICKLE_FILE_PATH = os.path.join(CURRENT_DIR, 'usgaap-concepts.pickle')
    _pool = {}

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def _parse_concepts_to_pool(cls):
        concept_file_path = os.path.join(cls.CURRENT_DIR, 'us-gaap', 'concepts_2014.csv')
        if not os.path.isfile(concept_file_path):
            raise IOError('Concept file does not exist in {0}'.format(concept_file_path))
        with open(concept_file_path) as f:
            for line in f:
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                line = line.strip()
                tokens = line.split('|')
                tokens = tokens[1:]     # remove the first token which is id
                if len(tokens) != 11:
                    diff = 11 - len(tokens)
                    tokens.extend([''] * diff)
                c = UsGaapConcept.create_instance(tokens)
                if not c:
                    continue
                cls._pool[c.tag.upper()] = c

    @classmethod
    def get(cls, tag):
        """
        tag format is <prefix>:<name>, eg. dei:DocumentType
        """
        if not cls._pool:
            cls._parse_concepts_to_pool()
        if tag.upper() not in cls._pool:
            return None
        return cls._pool[tag.upper()]

    @classmethod
    def get_all_tags(cls):
        if not cls._pool:
            cls._parse_concepts_to_pool()
        return sorted([x.tag for x in cls._pool.values()])

    @classmethod
    def get_pool(cls):
        if not cls._pool:
            cls._parse_concepts_to_pool()
        return cls._pool

    @classmethod
    def get_documentation(cls, tag):
        """
        Given a tag in <prefix>:<name> format, return its documentation
        """
        if not tag:
            return ''
        c = cls.get(tag)
        return c.documentation if c else ''

if __name__ == '__main__':
    # UsGaapConceptPool._load_pickle()
    # obj = UsGaapConceptPool.get('dei:documenttype')
    print UsGaapConceptPool.get_documentation('us-gaap:assets')
