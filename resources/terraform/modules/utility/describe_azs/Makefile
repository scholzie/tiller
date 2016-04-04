.PHONEY: all

all: variables.tf.json

variables.tf.json:
	python describe_azs.py

clean:
	rm -f variables.tf.json