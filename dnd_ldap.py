import ldap
import re
import string

default_attributes = ['cn', 'mail', 'dndDeptclass', 'eduPersonAffiliation', 'dndAssignedNetid', 'dndHinmanaddr'] 

word_boundary = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
l = None

def retry_lookup(query):
    for i in range(5):
        response = lookup(query)
        if response is not None:
            return response
    return None

def lookup(query,attribs=default_attributes):
    global l
    response = []

    if l is None:
        try:
            l = ldap.ldapobject.ReconnectLDAPObject('ldap://ldap.dartmouth.edu')
            l.simple_bind_s("", "")
        except ldap.LDAPError, error_message:
            l = None
            print "Error establishing LDAP connection"
            return None

    baseDN = "dc=dartmouth, dc=edu"
    terms = word_boundary.split(query.strip())
    
    ldap_query = "(&"
    for term in terms:
        term = (re.sub("^|$", "*", term))
        ldap_query += "(|(cn="+ term + ")(nickname="+ term +")(dndDeptclass="+ term +"))"
    ldap_query += ")"

    print ldap_query

    try:
        results = l.search_st(baseDN, ldap.SCOPE_SUBTREE, ldap_query, attribs, timeout=1)
        for r in results:
            response.append(r[1])
    except ldap.LDAPError, e:
        print "LDAP search error:"
        print e
        return None
    
    if response is None:
        print "Empty response"
        return None
    else:
        return format_response(response)

def format_response(response):
    return [ format_result(result) for result in response ]

def strip_singleton(a):
    if len(a) == 1:
        return a[0]
    elif len(a) > 1:
        return a
    else:
        return None

key_map = {
        'mail':'Email',
        'dndAssignedNetid':'Net ID',
        'cn':'Name',
        'dndHinmanaddr':'Hinman',
        'dndDeptclass':'Class',
        'eduPersonAffiliation':'Affiliation'
}
def format_result(result, mapping=key_map):
    if 'eduPersonAffiliation' in result:
        if ('Alum' in result['eduPersonAffiliation']) and ('Student' in result['eduPersonAffiliation']):
            result['eduPersonAffiliation'].remove('Alum')
        result['eduPersonAffiliation'] = ' & '.join(result['eduPersonAffiliation'])

    result = { new_k : strip_singleton(result.get(old_k, [])) for old_k, new_k in mapping.iteritems() }
    
    if result['Hinman'] is not None:
        m = re.search('(\d+)', result['Hinman'])
        if m is None:
            result['Hinman'] = "n/a"
        else:
            result['Hinman'] = m.group(0)
    else:
        result['Hinman'] = "n/a"
        
    none_to_emptystr = lambda x: "" if (x is None) else x
    result = { key : none_to_emptystr(val) for key, val in result.iteritems() }
    return result
