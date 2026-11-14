from google.cloud import bigquery

import harness
import load_to_bq


def main():
    out_path = harness.main()
    client = bigquery.Client(project=load_to_bq.PROJECT)
    load_to_bq.load_file(client, out_path)


if __name__ == "__main__":
    main()