import os
import sys
import subprocess

def get_short_path(long_path):

    if os.name == 'nt' and ' ' in long_path:
        try:
            output = subprocess.check_output(f'cmd /c "for %I in ("{long_path}") do @echo %~sI"', shell=True)
            return output.decode('utf-8').strip()
        except Exception:
            pass
    return long_path

python_path = get_short_path(sys.executable)

os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

print("Using Safe Python Path:", python_path)

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .master("local[1]")
    .appName("CheckSetup")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)

print("Spark version:", spark.version)
df = spark.createDataFrame([(1, "ok"), (2, "ok")], ["id", "status"])
df.show()
spark.stop()
    