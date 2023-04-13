import logging
from .Client import Client
from .Exceptions import ProjectNotFound

logger = logging.getLogger(__name__)

class Client(Client):
    def get_item_by(self, url, match_criteria, match_type="exact", page_size=250, **kwargs):
        """GET the first object whose attributes (key/value pairs) match
        the supplied match criteria

        Args:
            url : pointing to the RESTful set of objects, e.g. "/api/projects"
            match_criteria (dict): key/value pairs to match an object
            match_type (str): Can be one of "exact", "partial", or "fuzzy"

        Returns:
            REST API Object: a matching REST API object or None

        Raises:
        """
        for i in self.get_items(url, page_size=page_size, **kwargs):
            if match_type == 'exact':
                if all([i[k] == match_criteria[k] for k in match_criteria.keys()]):
                    return i
            elif match_type == 'partial':
                match_results = []
                for k in match_criteria.keys():
                    if isinstance(i[k], str):
                        match_results.append(match_criteria[k] in i[k])
                    else:
                        match_results.append(match_criteria[k] == i[k])
                if all(match_results):
                    return i                
            elif match_type == 'fuzzy':
                # Use Python fuzzy matching libs?
                pass
            else:
                # raise something?
                pass