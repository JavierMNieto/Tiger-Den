PROJECT_NAME := "tigerden"
MANAGE := ${PROJECT_NAME}/manage.py
FIXTURES := ${PROJECT_NAME}/fixtures

.PHONY: loaddata


all: build
	

initial-setup:
	@python ${MANAGE} loaddata ${FIXTURES}/attribute_option_groups.json \
								${FIXTURES}/options.json \
								${FIXTURES}/product_classes.json \
								${FIXTURES}/products.json \
								${FIXTURES}/categories.json \
								${FIXTURES}/product_categories.json \
								${FIXTURES}/product_images.json \
								${FIXTURES}/account_types.json \
								${FIXTURES}/accounts.json