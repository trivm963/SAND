def find_path(es, host1, host2, ipv6, date, pair):
    """
    **change this**
    Get list of hops for
    host1 : Source 1 (String)
    host2: Destination 1(String) 
    host3 : Source 2 (String)
    host4: Destination 2(String) 
    ipv6: (Bool)
    """    
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
    
    data12 = es.search('ps_trace', body=query12)  
    if not data12['aggregations']['the_hash']['buckets']:
        print("no such record, pair " + str(pair))
        return
    hash12 = data12['aggregations']['the_hash']['buckets'][0]['key']
    
    if (hash11 == hash12):
        same = True
    else:
        same = False
    
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
    
    the_data = []
    the_data.append(same)
    the_data.append(the_hops11)
        
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
        
        the_data.append(the_hops12)
    
    return the_data
    #Format: the_data[same][the_hops11][the_hops12]
    #Format: the_hops1x[([from0][to0][hop0])][...]...
    #[([from(n-1)][to(n-1)][hop(n-1)])] ie a tuple!
    #Make less redundant? (wrt before/after queries similar) 
    
    
def common_hops(es, ipv6, date, *sites):
    if (len(sites) % 2 == 1):
        print("Error: sites must be in host dest PAIRS")
        return
    if (len(sites) < 3):
        print("Error: must have at least two pairs")
        return
    n = 0
    pair = 1
    all_data = []
    while n < len(sites):
        all_data.append(find_path(es, sites[n], sites[n+1], ipv6, date, pair)) 
        pair += 1 
        n += 2
    
    after_exists = False
    
    print("Pairs with a differing path before and after given time:")
    
    for x in range(len(all_data)):
        if (all_data[x][0] == False):
            after_exists = True
            print(x)
    
    if (after_exists == False):
        print("None" + '\n')
        
    
    common_arr = [] #before
    common_arr2 = [] #existing afters

    for x in range(len(all_data[0][1])):
        for y in range(len(all_data[1][1])):
            if ((all_data[0][1][x][0] == all_data[1][1][y][0]) and (all_data[0][1][x][1] == all_data[1][1][y][1])):
                common_arr.append([all_data[0][1][x][0], all_data[0][1][x][1], all_data[0][1][x][2], all_data[1][1][y][2]])
                #element of common_arr: [from, to, place in path 1, place in path 2]
    if (after_exists == True):
        if (all_data[0][0] == False):
            if (all_data[1][0] == False):
                for x in range(len(all_data[0][2])):
                    for y in range(len(all_data[1][2])):
                        if ((all_data[0][2][x][0] == all_data[1][2][y][0]) and (all_data[0][2][x][1] == all_data[1][2][y][1])):
                            common_arr2.append([all_data[0][2][x][0], all_data[0][2][x][1], all_data[0][2][x][2], all_data[1][2][y][2]])
            else:
                for x in range(len(all_data[0][2])):
                    for y in range(len(all_data[1][1])):
                        if ((all_data[0][2][x][0] == all_data[1][1][y][0]) and (all_data[0][2][x][1] == all_data[1][1][y][1])):
                            common_arr2.append([all_data[0][2][x][0], all_data[0][2][x][1], all_data[0][2][x][2], all_data[1][1][y][2]])
        elif (all_data[1][0] == False):
            for x in range(len(all_data[0][1])):
                for y in range(len(all_data[1][2])):
                    if ((all_data[0][1][x][0] == all_data[1][2][y][0]) and (all_data[0][1][x][1] == all_data[1][2][y][1])):
                        common_arr2.append([all_data[0][1][x][0], all_data[0][1][x][1], all_data[0][1][x][2], all_data[1][2][y][2]])
        else:
            common_arr2.append(common_arr[0])

    pair -= 3
    
    while pair > 0:
        for x in range(len(all_data[pair][1])):
            found = False
            for y in range(len(common_arr)):
                if ((all_data[pair][1][x][0] == common_arr[y][0]) and (all_data[pair][1][x][1] == common_arr[y][1])):
                    common_arr[y].append(all_data[pair][1][x][2])
                    found = True
                if ((y == (len(common_arr) - 1)) and (found == False)):
                    common_arr.remove(common_arr[y])

        if (after_exists == True):
            if (all_data[pair][0] == False):
                for x in range(len(all_data[pair][2])):
                    found = False
                    for y in range(len(common_arr2)):
                        if ((all_data[pair][2][x][0] == common_arr2[y][0]) and (all_data[pair][2][x][1] == common_arr2[y][1])):
                            common_arr2[y].append(all_data[pair][2][x][2])
                            found = True
                        if ((y == (len(common_arr2) - 1)) and (found == False)):
                            common_arr2.remove(common_arr2[y])  
            else:
                for x in range(len(all_data[pair][1])):
                    found = False
                    for y in range(len(common_arr2)):
                        if ((all_data[pair][1][x][0] == common_arr2[y][0]) and (all_data[pair][1][x][1] == common_arr2[y][1])):
                            common_arr2[y].append(all_data[pair][1][x][2])
                            found = True
                        if ((y == (len(common_arr2) - 1)) and (found == False)):
                            common_arr2.remove(common_arr2[y])    
        pair -= 1
        
    n_sites = 2
    print("Number of common hops: ", len(common_arr), '\n')
    for x in range(len(common_arr)):
        print(common_arr[x][0], ", ", common_arr[x][1], ", ", end =" ")
        while n_sites < ((len(sites)/2) + 1):
            print(common_arr[x][n_sites], ", ", end =" ")
            n_sites += 1
        print(common_arr[x][n_sites])
        n_sites = 2
        
    if (after_exists == True):    
        n_sites = 2
        print(len(common_arr2))
        for x in range(len(common_arr2)):
            print(common_arr2[x][0], ", ", common_arr2[x][1], ", ", end =" ")
            while n_sites < ((len(sites)/2) + 1):
                print(common_arr2[x][n_sites], ", ", end =" ")
                n_sites += 1
            print(common_arr2[x][n_sites])
            n_sites = 2
        
    
        
    #TODO: Testing  
