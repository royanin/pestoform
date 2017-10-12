import json
import shelve

def find_acad_domain(check_domain):    
    inst_db = shelve.open("inst_db.dat", "r")
    dom_len = len(check_domain.split("."))
    while(dom_len>=2):
        try:
            if(inst_db[check_domain]):
                #print inst_db[check_domain]
                loc_len = len(inst_db[check_domain])
                loc = []
                for i in range (loc_len):
                    loc.append(inst_db[check_domain][i][2])
                #if loc_len > 1:
                u_loc = list(set(loc))
                if len(u_loc)>1:
                    return("Multi_country")
                    break
                else:
                    return(u_loc[0])

        except KeyError:
            lst = check_domain.split(".")
            del lst[0]
            check_domain = (".").join(lst[:])
            dom_len = dom_len - 1
            #print dom_len, check_domain
        

if __name__ == '__main__':
    inp=raw_input("Please enter a domain name:\n")
    print find_acad_domain(inp)

