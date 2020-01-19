def common_hops(es, host1, host2, host3, host4, ipv6):
    """
    Get list of hops for
    host1 : Source 1 (String)
    host2: Destination 1(String) 
    host3 : Source 2 (String)
    host4: Destination 2(String) 
    ipv6: (Bool)
    """
    
    query1 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "src_host": {
                  "value": host1
                }
              }
            },
            {
              "term": {
                "dest_host": {
                  "value": host2
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
                "field": "route-sha1",
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
                "src_host": {
                  "value": host3
                }
              }
            },
            {
              "term": {
                "dest_host": {
                  "value": host4
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
                "field": "route-sha1",
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
                "route-sha1": {
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
        the_hops1.append([hops1[x], hops1[x+1], x])
        
    
    query4 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "route-sha1": {
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
        the_hops2.append([hops2[x], hops2[x+1], x])
        
    
        
    common_hops = []   
    
    for x in range(len(hops1) - 1):
        for y in range(len(hops2) - 1):
            if ((the_hops1[x][0] == the_hops2[y][0]) and (the_hops1[x][1] == the_hops2[y][1])):
                the_hops1[x].append(the_hops2[y][2])
                common_hops.append(the_hops1[x])
                
    
    print(len(common_hops))
    for x in range(len(common_hops)):
        print(common_hops[x][0], ", ", common_hops[x][1], ", ", common_hops[x][2], ", ", common_hops[x][3])
    
     
