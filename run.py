__author__ = 'baidu'
import subprocess , sys
def main():
    if len(sys.argv) != 4:
        print 'python run.py {ins-fea} {train} {pred}'
        return
    insfea = int(sys.argv[1])
    train= int(sys.argv[2])
    pred= int(sys.argv[3])

    if insfea == 1:
        print 'ins-fea'
        subprocess.check_call("python ins_prepare.py merge.ini",shell=True)
        subprocess.check_call("python ins_test_prepare.py merge.ini",shell=True)
        subprocess.check_call("python expand_pred_sample.py merge.ini",shell=True)
    if train ==1 :
        print 'train'
        cmds = [
            'rm -rf ./test_sample/*.buffer',
            'rm -rf ./train_sample/*.buffer',
          #  './xgboost train.conf  &> train.dem.log',
          #  './xgboost train.sup.conf &> train.sup.log',
            ' ./xgboost train.gap.conf &>train.gap.log',
            './xgboost train.gap.bin.conf &>train.gap.bin.log',

        ]
        for cmd in cmds:
            subprocess.check_call(cmd , shell=True)
    if pred ==1:
        print 'pred..'
        cmds = [
            'rm -rf ./test_sample/*.buffer',
            'rm -rf ./train_sample/*.buffer',
            './xgboost pred.conf &>pred.dem.log',
            './xgboost pred.sup.conf &>pred.sup.log',
            './xgboost pred.gap.conf &>pred.gap.log',
            './xgboost eval.mape.conf &>eval.mape.log' ,

                './xgboost pred.gap.bin.conf &>pred.gap.bin.log ',

            'python bingo.py merge.ini',
            'python eval_mape.py merge.ini',
            "cat ./test_sample/bingo |awk -F , '{print $1\",\"$2\",\"$3}' >./test_sample/bingo.b",
            "cat ./test_sample/bingo |awk -F , '{print $1\",\"$2\",\"$4}' >./test_sample/bingo.gap",
            'cp ./test_sample/bingo.b  ~/baipeng/transfer-data/',
            'cp ./test_sample/bingo.gap  ~/baipeng/transfer-data/',
            'python ensemble_bin_reg.py merge.ini'
        ]
        for cmd in cmds:
            subprocess.check_call(cmd,shell=True)

    print 'done'


if __name__ == "__main__":
    main()
