import pandas as pd
import os
import glob
import argparse


def correct(df,file):
    cols = df.columns
    for suffix in [x.split('_',1)[1] for x in cols if 'FileName' in x]:
        assert len([x.split('_',1)[1] for x in cols if 'FileName' in x]) == len(set([x.split('_',1)[1] for x in cols if 'FileName' in x])), f"{file} failed"
        if df[f'PathName_{suffix}'][0].endswith('/'):
            df[f'URL_{suffix}'] = df[f'PathName_{suffix}'] + df[f'FileName_{suffix}']
        else:
            df[f'URL_{suffix}'] = df[f'PathName_{suffix}'] + '/' + df[f'FileName_{suffix}']
        df.drop(columns=[f'PathName_{suffix}',f'FileName_{suffix}'],inplace=True)
        # move URL columns to the front of the dataframe
        col = df.pop(f'URL_{suffix}')
        df.insert(0, col.name, col)
    df.replace('/home/ubuntu/bucket/','s3://cellpainting-gallery/',inplace=True,regex=True)
    return df


def main():
    ## examples for in_path and out_path
    # in_path = '/Local/Path/load_data_csv_orig/' # as output by pe2loaddata_cpg
    # out_path = '/Local/Path/load_data_csv/' # output of this script

    # Simple argparse just to allow basic customization without editing script
    parser = argparse.ArgumentParser(description="Process load_data csv for CPG format")
    parser.add_argument("--input_path", type=str, 
                        help=f"Input path")
    parser.add_argument("--out_path", type=str,
                        help=f"Output path")
    args = parser.parse_args()

    in_path = args.input_path
    out_path = args.out_path

    print(os.path.join(in_path,'*','*','*.csv'))
    print(glob.glob(os.path.join(in_path,'*','*','*.csv')))

    count = 0
    for file in glob.glob(os.path.join(in_path,'*','*','*.csv')):
        df = pd.read_csv(file)
        df = correct(df,file)
        # if csv's were made from an internal location, you'll need a find and replace
        # if csv's were made from files already on CPG, the replace can remain commented out
        # df.replace(f'projects/DATE_PROJECTNAME','CPG_IDENTIFIER/SOURCE/images',inplace=True,regex=True)
        outfile = file.replace(in_path,out_path)
        if not os.path.exists(outfile.rsplit('/',1)[0]):
            os.makedirs(outfile.rsplit('/',1)[0],exist_ok=True)
        df.to_csv(outfile,index=False)
        count += 1

    print(f'Corrected {count} files')


if __name__ == "__main__":
    main()