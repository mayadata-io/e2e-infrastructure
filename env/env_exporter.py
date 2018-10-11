# HOW TO RUN:
# export TEST=$(eval python env_exporter.py -o mapi)
import os
import argparse

# maya
def getMaya(filename, opt):
    file = open(filename, "r")
    for line in file:
        data = line.split(',')
        # print(data[2].split('='))
        repo = data[2].split('=')
        commit = data[4].split('=')
        if repo[1] == 'maya':
            mayaDetails = ['maya', commit[1].rstrip('\n')]
            file.close()
            if opt == 'mapi':
                return 'openebs/'+'m-apiserver'+':'+mayaDetails[1]
            elif opt == 'iovolume':
                return 'openebs/'+'m-exporter'+':'+mayaDetails[1]
    file.close() 
    return None
    
# jiva
def getJiva(filename, opt):
    file = open(filename, "r")
    for line in file:
        data = line.split(',')
        # print(data[2].split('='))
        repo = data[2].split('=')
        commit = data[4].split('=')
        if repo[1] == 'jiva':
            jivaDetails = ['jiva', commit[1].rstrip('\n')]
            file.close() 
            if opt == 'jcontroller':
                return 'openebs/'+'jiva'+':'+jivaDetails[1]
            elif opt == 'jreplica':
                return 'openebs/'+'jiva'+':'+jivaDetails[1]
    file.close() 
    return None

# cstor
def getCstor(filename):
    file = open(filename, "r")
    for line in file:
        data = line.split(',')
        # print(data)
        repo = data[2].split('=') #data[2] has repo info
        commit = data[4].split('=') # data[4] has commit info
        if repo[1] == 'cstor':
            cstorDetails = ['cstor', commit[1].rstrip('\n')]
            file.close()
            return cstorDetails
    file.close() 
    return None

def run(option):
    filename = "../baseline/baseline"
    if (option == 'mapi') or (option == 'iovolume'):
        maya = getMaya(filename, option)
        print maya
        return
    elif (option == 'jcontroller') or (option == 'jreplica'):
        jiva = getJiva(filename, option)
        print jiva
        return
    elif option == 'cstor':
        cstor = getCstor(filename)
        print cstor
        return
    else:
        print 'Invalid Entry!!'
        return
    # print maya
    # print jiva
    # print cstor
    # print option
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='returns')
    parser.add_argument('-o','--option', help='Enter the repo name', required=True)
    args = vars(parser.parse_args())

    run(args['option'])