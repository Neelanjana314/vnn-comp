import matlab.engine
import os
import scipy.io as sio
import argparse

def executeCifar(filePath, netfile, epsilon, reachMethod, N, t_out, rF):
    # start matlab engine
    eng = matlab.engine.start_matlab()
    eng.addpath(filePath, nargout=0)
    rb = eng.zeros(1,N,nargout=1)
    vt = eng.zeros(1,N,nargout=1)
    filename = filePath+'/incorrectIndex_'+str(int(epsilon))+'_255.mat'
    inCorrectClass =sio.loadmat(filename)
    #print('inCorrectClass: ',inCorrectClass)
    
    netfile = filePath + '/' + netfile

    for i in range(1,N+1):
        print("\n===============================Image Id: %d ====================================" % (i));
        
        if i in inCorrectClass['incorrectClasidied']:
            rb[0][i-1]=4;
            vt[0][i-1]=0;
            print('incorrectlyclassified');
        else:
            #print('in else')
            try:
                future = eng.verifyCifar(netfile,epsilon,i,reachMethod,rF,nargout=2,background = True);
                rb1 ,vt1 = future.result(timeout = t_out);
                if rb1 == 2 and rF != 0 :
                    print('trying again with diff rF')
                    future.cancel;
                    try:
                       rF = 0;
                       future = eng.verifyCifar(netfile,epsilon,i,reachMethod,rF,nargout=2,background = True);
                       rb1 ,vt1 = future.result(timeout = t_out);
                    except matlab.engine.TimeoutError:
                        print("timeout");
                        future.cancel;
                        eng.quit();
                        eng = matlab.engine.start_matlab();
                        eng.addpath(filePath, nargout=0);
                        print("out from prev image");
                        rb1 =3;
                        vt1 =t_out;  
                rb[0][i-1]=rb1
                vt[0][i-1]=vt1;
            except matlab.engine.TimeoutError:
                print("timeout");
                future.cancel;
                eng.quit();
                eng = matlab.engine.start_matlab();
                eng.addpath(filePath, nargout=0);
                print("out from prev image");
                rb[0][i-1]=3;
                vt[0][i-1]=t_out;
    eng.saveDataCifar(epsilon,rb,vt,nargout=0);


def main():
    parser = argparse.ArgumentParser(description ='script to execute CIFAR 10')
    parser.add_argument('filePath')
    parser.add_argument('netfile')
    parser.add_argument('epsilon', type = float)
    parser.add_argument('t_out', type = int, default = 300)
    parser.add_argument('relaxFactor', type = float, default = 1)
    args = parser.parse_args()
    executeCifar(args.filePath, args.netfile, args.epsilon, 'approx-star',100, args.t_out,args.relaxFactor)

if __name__ == "__main__":
    main()
