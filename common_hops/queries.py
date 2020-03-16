def find_path(es, host1, host2, ipv6, date, pair):
    """
    Get list of hops for
    host1 : Source 1 (String)
    host2: Destination 1(String) 
    host3 : Source 2 (String)
    host4: Destination 2(String) 
    ipv6: (Bool)
    """    
    querya1 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "range": {
                "timestamp": {
                  "gte": date
                }
              }
            },
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
            "after_time": {
              "min": {
                "field": "timestamp"
              }
            }
          }
        }
    
    dataa1 = es.search('ps_trace', body=querya1)  
    if not dataa1['aggregations']['after_time']['value']:
        print("time after error")
        return
    timea = dataa1['aggregations']['after_time']['value']
    
    queryb1 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
             {
              "range": {
                "timestamp": {
                  "lte": date
                }
              }
            },
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
            "before_time": {
              "max": {
                "field": "timestamp"
              }
            }
          }
        }
    
    datab1 = es.search('ps_trace', body=queryb1)  
    if not datab1['aggregations']['before_time']['value']:
        print("time before error")
        return
    timeb = datab1['aggregations']['before_time']['value']
  
    query11 = {
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
                "timestamp": {
                  "value": str(timea)
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
    
    data11 = es.search('ps_trace', body=query11)  
    if not data11['aggregations']['the_hash']['buckets']:
        print("no such record, pair " + str(pair))
        return
    hash11 = data11['aggregations']['the_hash']['buckets'][0]['key']
    
    query12 = {
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
                "timestamp": {
                  "value": str(timeb)
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
    
    data12 = es.search('ps_trace', body=query12)  
    if not data12['aggregations']['the_hash']['buckets']:
        print("no such record, pair " + str(pair))
        return
    hash12 = data12['aggregations']['the_hash']['buckets'][0]['key']
    
    if (hash11 == hash12):
        same = True
        print("paths before and after input time are same for pair " + str(pair))
    else:
        same = False
        print("paths before and after input time differ for pair " + str(pair))
        #TODO: Ask user which paths they require
        #As of now, getting both paths
    
    query31 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "route-sha1": {
                  "value": hash11
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
    raw11 = es.search('ps_trace', body=query31) 
        
    hops11 = raw11['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
    the_hops11 = []
    
    for x in range(len(hops11) - 1):
        the_hops11.append([hops11[x], hops11[x+1], x])
        
    if (same == False):
        
        query32 = {
          "size": 0,
          "query": {
            "bool": {
              "filter": [
                {
                  "term": {
                    "route-sha1": {
                      "value": hash12
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
        raw12 = es.search('ps_trace', body=query32) 
        
        hops12 = raw12['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
        the_hops12 = []
    
        for x in range(len(hops12) - 1):
            the_hops12.append([hops12[x], hops12[x+1], x])
    
    #Make less redundant? (wrt before/after queries similar)
    #TODO: Return the data!! (once figured out how to where to handle before/after; are we doing both, only one??)
    
    
def common_hops(es, ipv6, date, *sites):
    if (len(sites) % 2 == 1):
        print("Error: sites must be in host dest PAIRS")
        return
    n = 0
    pair = 1
    while n < len(sites):
        find_path(es, sites[n], sites[n+1], ipv6, date, pair) #TODO: put this data into array
        pair += 1 
        n += 2
    
    return #for now
    #TODO: Generalised method for comparing paths; old one for two pairs below and DOES NOT WORK NOW
    common_hops_arr = []   

    for x in range(len(hops1) - 1):
        for y in range(len(hops2) - 1):
            if ((the_hops1[x][0] == the_hops2[y][0]) and (the_hops1[x][1] == the_hops2[y][1])):
                the_hops1[x].append(the_hops2[y][2])
                common_hops_arr.append(the_hops1[x])


    print(len(common_hops_arr))
    for x in range(len(common_hops_arr)):
        print(common_hops_arr[x][0], ", ", common_hops_arr[x][1], ", ", common_hops_arr[x][2], ", ", common_hops_arr[x][3])
    
     
