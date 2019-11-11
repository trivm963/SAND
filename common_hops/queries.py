def common_hops(es, site1, site2, site3, site4, ipv6):
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
    
    data1 = es.search('ps_trace', body=query1)  
    if not data1['aggregations']['the_hash']['buckets']:
        print("no such record, 1st pair")
        return
    hash1 = data1['aggregations']['the_hash']['buckets'][0]['key']
    
    query2 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "src_site": {
                  "value": site3
                }
              }
            },
            {
              "term": {
                "dest_site": {
                  "value": site4
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
    data2 = es.search('ps_trace', body=query2)  
    if not data2['aggregations']['the_hash']['buckets']:
        print("no such record, 2nd pair")
        return
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
    raw1 = es.search('ps_trace', body=query3) 
    hops1 = raw1['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
    the_hops1 = []
    
    for x in range(len(hops1) - 1):
        the_hops1.append([hops1[x], hops1[x+1]])
        
    
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
    raw2 = es.search('ps_trace', body=query4) 
    hops2 = raw2['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
    the_hops2 = []
    
    for x in range(len(hops2) - 1):
        the_hops2.append([hops2[x], hops2[x+1]])
        
    common_hops = []   
    
    for x in range(len(hops1) - 1):
        for y in range(len(hops2) - 1):
            if (the_hops1[x] == the_hops2[y]):
                common_hops.append(the_hops1[x])
                
    
    print(len(common_hops))
    for x in range(len(common_hops)):
        print(common_hops[x][0], ", ", common_hops[x][1])
    
     
