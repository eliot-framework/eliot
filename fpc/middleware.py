from django.conf import settings
from django.db import connection
import logging
import re


class MinifyHTMLMiddleware(object):
    """
    Strips leading and trailing whitespace from response content.
    """

    def __init__(self):
        self.whitespace = re.compile('^\s*\n', re.MULTILINE)
        #self.htmlcomments = re.compile('\<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)\>')
        # self.whitespace_lead = re.compile('^\s+', re.MULTILINE)
        # self.whitespace_trail = re.compile('\s+$', re.MULTILINE)


    def process_response(self, request, response):
        if "text" in response['Content-Type']:
            if hasattr(self, 'whitespace_lead'):
                response.content = self.whitespace_lead.sub('', response.content)
            if hasattr(self, 'whitespace_trail'):
                response.content = self.whitespace_trail.sub('\n', response.content)
            # Uncomment the next line to remove empty lines
            if hasattr(self, 'whitespace'):
                response.content = self.whitespace.sub('', str(response.content))
                #response.content = self.htmlcomments.sub('', response.content)
            return response
        else:
            return response    
    
 
 
 
 
class JsonAsHTML(object):
    '''
    View a JSON response in your browser as HTML
    Useful for viewing stats using Django Debug Toolbar
     
    This middleware should be place AFTER Django Debug Toolbar middleware
    '''
     
    def process_response(self, request, response):
     
        # not for production or production like environment
        if not settings.DEBUG:
            return response
         
        # do nothing for actual ajax requests
        if request.is_ajax():
            return response
         
        # only do something if this is a json response
        if 'application/json' in response['Content-Type'].lower():
            title = 'JSON as HTML Middleware for: %s' % request.get_full_path()
            response.content = '<html><head><title>%s</title></head><body>%s</body></html>' % (title, response.content)
            response['Content-Type'] = 'text/html'
        
        return response
    



class MonitoraSQLMiddleware(object):
    """
    Monitora os SQLs executados
    """
    
    logger = None;

    def __init__(self):
        self.logger = logging.getLogger('eliot.fpc')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())


    def process_response(self, request, response):
        if settings.DEBUG and response.status_code == 200:
            total_time = 0
            for query in connection.queries:
                query_time = query.get('time')
                if query_time is None:
                    # django-debug-toolbar monkeypatches the connection
                    # cursor wrapper and adds extra information in each
                    # item in connection.queries. The query time is stored
                    # under the key "duration" rather than "time" and is
                    # in milliseconds, not seconds.
                    query_time = query.get('duration', 0) / 1000
                total_time += float(query_time)
            
            self.logger.debug('\nSTATS: %s queries run, total %s seconds' % (len(connection.queries), total_time))
            for query in connection.queries:
                self.logger.debug(query["sql"])
        return response