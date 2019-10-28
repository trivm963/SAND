def symmetry(es, index, site1, site2, ipv6):
    """
    Get list of hops for
    src : Source (String)
    dest: Destination (String) 
    """
    
    query1 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "src_site": {
                  "value": site1
                }
              }
            },
            {
              "term": {
                "dest_site": {
                  "value": site2
                }
              }
            },
              {
              "term": {
                "ipv6": {
                  "value": ipv6
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "the_hash": {
              "terms": {
                "field": "hash",
                "order": {"_count" : "desc"},
                "size": 1
              }
            }
          }
        }
    
    data1 = es.search(index, body=query1)  
    if not data1['aggregations']['the_hash']['buckets']:
        return False
    hash1 = data1['aggregations']['the_hash']['buckets'][0]['key']
    
    query2 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "src_site": {
                  "value": site2
                }
              }
            },
            {
              "term": {
                "dest_site": {
                  "value": site1
                }
              }
            },
              {
              "term": {
                "ipv6": {
                  "value": ipv6
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "the_hash": {
              "terms": {
                "field": "hash",
                "order": {"_count" : "desc"},
                "size": 1
              }
            }
          }
        }
    data2 = es.search(index, body=query2)  
    if not data2['aggregations']['the_hash']['buckets']:
        return False
    hash2 = data2['aggregations']['the_hash']['buckets'][0]['key']


    query3 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "hash": {
                  "value": hash1
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "hops_list": {
              "top_hits": {
                "size": 1
              }
            }
          }
        }
    raw1 = es.search(index, body=query3) 
    hops1 = raw1['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
    
    for x in range(len(hops1)):
        print(hops1[x])
    
    query4 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "hash": {
                  "value": hash2
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "hops_list": {
              "top_hits": {
                "size": 1
              }
            }
          }
        }
    raw2 = es.search(index, body=query4) 
    hops2 = raw2['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
    print("***")
    
    for x in range(len(hops2)):
        print(hops2[x])
        
    print("***")
    
    if (len(hops1) != len(hops2)):
        return False
    else:
        for x in range(len(hops1) - 1):
            if (hops1[x] != hops2[len(hops1) - 1 - x]):
                return False
        return True
    
    