def find_path(es, host1, host2, ipv6, date, mil, pair):   
    #Find the time directly before input time
    queryb1 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "range": {
                "timestamp": {
                  "lte": date,
                  "gte": int(date) - mil
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
                "destination_reached": {
                  "value": True
                }
              }
            },
            {
              "term": {
                "path_complete": {
                  "value": True
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
    datab1 = es.search(index='ps_trace', body=queryb1)

    if not datab1['aggregations']['before_time']['value']:
        print("could not find such a path before input time. try different inputs?")
        return False
    timeb = datab1['aggregations']['before_time']['value']

    
    #Find the time directly after input time
    querya1 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
             {
              "range": {
                "timestamp": {
                  "gte": date,
                  "lte": int(date) + mil
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
                "destination_reached": {
                  "value": True
                }
              }
            },
            {
              "term": {
                "path_complete": {
                  "value": True
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
    
    dataa1 = es.search(index='ps_trace', body=querya1)  
    if not dataa1['aggregations']['after_time']['value']:
        print("could not find such a path after input time. try different inputs?")
        #Q: tho like if it doesn't exist, should we just use default before path????
        return False
    timea = dataa1['aggregations']['after_time']['value']
   
    #Find hash of path at time before
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
                "destination_reached": {
                  "value": True
                }
              }
            },
            {
              "term": {
                "path_complete": {
                  "value": True
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
    
    data11 = es.search(index='ps_trace', body=query11)  
    if not data11['aggregations']['the_hash']['buckets']:
        print("no such record, pair " + str(pair))
        return False
    hash11 = data11['aggregations']['the_hash']['buckets'][0]['key']
    #if (check_bools(es, hash11, pair) == False):
     #   return False
    
    #Find hash of path at time before
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
                "destination_reached": {
                  "value": True
                }
              }
            },
            {
              "term": {
                "path_complete": {
                  "value": True
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
    
    data12 = es.search(index='ps_trace', body=query12)  
    if not data12['aggregations']['the_hash']['buckets']:
        print("no such record, pair " + str(pair))
        return False
    hash12 = data12['aggregations']['the_hash']['buckets'][0]['key']
    #if (check_bools(es, hash11, pair) == False): #TODO
     #   useb = True
    
    #Check whether the path before and after the input time are the same
    if (hash11 == hash12): #or (useb == True)
        same = True
    else:
        same = False
    
    #Find dest ip (since dest is not included in hash)
    query15 = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
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
            "dest_ip": {
              "terms": {
                "field": "dest",
                "order": {"_count" : "desc"},
                "size": 1
              }
            }
          }
        }
    
    data15 = es.search(index='ps_trace', body=query15)  
    ip_d = data15['aggregations']['dest_ip']['buckets'][0]['key']
    
    #Find hop list associated with before hash (as it is default)
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
            },
            {
              "term": {
                "dest": {
                  "value": ip_d
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
    raw11 = es.search(index='ps_trace', body=query31) 
        
    hops11 = raw11['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
    the_hops11 = []
    
    for x in range(len(hops11) - 1):
        the_hops11.append([hops11[x], hops11[x+1], x])
    
    #Format: the_hops1x[([from0][to0][hop0])][...]...[([from(n-1)][to(n-1)][hop(n-1)])] ie a list of tuples!
    the_data = []
    the_data.append(same)
    the_data.append(the_hops11)
    
    #If after time is different, find hop list associated with after hash    
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
                },
                {
                  "term": {
                    "dest": {
                      "value": ip_d
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
        raw12 = es.search(index='ps_trace', body=query32) 
        
        hops12 = raw12['aggregations']['hops_list']['hits']['hits'][0]['_source']['hops']
        the_hops12 = []
    
        for x in range(len(hops12) - 1):
            the_hops12.append([hops12[x], hops12[x+1], x])
        
        the_data.append(the_hops12)
    
    return the_data
    #Format: the_data [same][the_hops11][the_hops12] (if the_hops12 exists)
    #Else, it is [same][the_hops11]. The [same] bool makes sure we don't go to [the_hops12] if it doesn't exist
       
    
def common_hops(es, ipv6, date, hrs, *sites):
    if (len(sites) % 2 == 1):
        print("Error: sites must be in host dest PAIRS")
        return
    if (len(sites) < 3):
        print("Error: must have at least two pairs")
        return
    n = 0
    pair = 1
    mil = hrs * 3600000
    all_data = []
    #Get paths/data for all pairs and save them in all_data, looping above function
    while n < len(sites):
        whatever = find_path(es, sites[n], sites[n+1], ipv6, date, mil, pair)
        if (whatever == False):
            return
        all_data.append(whatever) 
        pair += 1 
        n += 2
    
    after_exists = False #We won't run the after code if none exist
    
    print("Pairs with a differing path before and after given time:")
    
    #Find and output all pairs that have differing before and after paths
    for x in range(len(all_data)):
        if (all_data[x][0] == False):
            after_exists = True
            print(x)
    
    if (after_exists == False):
        print("None")
    
    print('\n')
        
    
    common_arr = [] #before
    common_arr2 = [] #existing afters, rest are before

    #Find the common hops between the first two pairs, and append to an array
    #element of common_arr: [from, to, place in path 1, place in path 2]
    for x in range(len(all_data[0][1])):
        for y in range(len(all_data[1][1])):
            if ((all_data[0][1][x][0] == all_data[1][1][y][0]) and (all_data[0][1][x][1] == all_data[1][1][y][1])):
                common_arr.append([all_data[0][1][x][0], all_data[0][1][x][1], all_data[0][1][x][2], all_data[1][1][y][2]])
    #Do the same for after common hops
    #The problem is the first pair and second pair may each both have a different after path, so there are four different combinations. Hence, mutually exclusive if statements
    #If a pair doesn't have a different after time, we append the 'before' path, as it is the same after (this also holds for the while loop below)
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
    
    #Compare each successive pair with the common_arr, altering it as appropriate
    #Same for common_arr2, but with the after paths
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
    
    #Output number of common hops followed by the list of common hops
    n_sites = 2
    print("Number of common hops: ", len(common_arr), '\n')
    for x in range(len(common_arr)):
        print(common_arr[x][0], ", ", common_arr[x][1], ", ", end =" ")
        while n_sites < ((len(sites)/2) + 1):
            print(common_arr[x][n_sites], ", ", end =" ")
            n_sites += 1
        print(common_arr[x][n_sites])
        n_sites = 2
    print('\n')    
    
    #Output number of after time common hops and list (if it exists)
    if (after_exists == True):    
        n_sites = 2
        print("Number of common hops (after time): ", len(common_arr2), '\n')
        for x in range(len(common_arr2)):
            print(common_arr2[x][0], ", ", common_arr2[x][1], ", ", end =" ")
            while n_sites < ((len(sites)/2) + 1):
                print(common_arr2[x][n_sites], ", ", end =" ")
                n_sites += 1
            print(common_arr2[x][n_sites])
            n_sites = 2
        
        #TODO: Testing

"""
Old check bools function. Keeping this here just in case!

def check_bools(es, hash_, pair):
    #method to check that destination_reached and path_complete are True while looping is False
    querydr = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "route-sha1": {
                  "value": hash_
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "dest_reach": {
              "terms": {
                "field": "destination_reached",
                "order": {"_count" : "desc"},
                "size": 1
              }
            }
          }
        }
    
    datadr = es.search(index='ps_trace', body=querydr)  
    dr = datadr['aggregations']['dest_reach']['buckets'][0]['key']
    if (dr == False):
        print("pair ", pair, " has not reached dest")
        return False
    
    querypc = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "route-sha1": {
                  "value": hash_
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "path_c": {
              "terms": {
                "field": "path_complete",
                "order": {"_count" : "desc"},
                "size": 1
              }
            }
          }
        }
    
    datapc = es.search(index='ps_trace', body=querypc)  
    pc = datapc['aggregations']['path_c']['buckets'][0]['key']
    if (pc == False):
        print("pair ", pair, " does not have a complete path")
        return False
    
    queryl = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "term": {
                "route-sha1": {
                  "value": hash_
                }
              }
            }
          ]
        }
      },
        "aggs": {
            "loop": {
              "terms": {
                "field": "looping",
                "order": {"_count" : "desc"},
                "size": 1
              }
            }
          }
        }
    
    datal = es.search(index='ps_trace', body=queryl)  
    loop = datal['aggregations']['loop']['buckets'][0]['key']
    if (loop == True):
        print("pair ", pair, " has looping")
        return False
   
    return True
 """   