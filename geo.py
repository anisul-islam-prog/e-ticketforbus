import json
import requests
import sys

if __name__ == '__main__':
	
	# The API key must be provided on the command line, abort otherwise. 
	api_key = 'AIzaSyCPboq3AlDsQJlfcOULCUqcNTHQ7bFseyQ'
	

	# Google Distance Matrix base URL to which all other parameters are attached
	base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

	# Google Distance Matrix domain-specific terms: origins and destinations
	origins = ['23.781083, 90.398910']
	destinations = ['23.780201, 90.410209']

	# Prepare the request details for the assembly into a request URL
	payload = {
		'origins' : '|'.join(origins),
		'destinations' : '|'.join(destinations), 
		'mode' : 'driving',
		'api_key' : api_key
	}

	# Assemble the URL and query the web service
	r = requests.get(base_url, params = payload)

	# Check the HTTP status code returned by the server. Only process the response, 
	# if the status code is 200 (OK in HTTP terms).
	if r.status_code != 200:
		print 'HTTP status code {} received, program terminated.'.format(r.status_code)
	else:
		try:
			# Try/catch block should capture the problems when loading JSON data, 
			# such as when JSON is broken. It won't, however, help much if JSON format
			# for this service has changed -- in that case, the dictionaries json.loads() produces
			# may not have some of the fields queried later. In a production system, some sort
			# of verification of JSON file structure is required before processing it. In XML
			# this role is performed by XML Schema.
			x = json.loads(r.text)

			# Now you can do as you please with the data structure stored in x.
			# Here, we print it as a Cartesian product.
			for isrc, src in enumerate(x['origin_addresses']):
				for idst, dst in enumerate(x['destination_addresses']):
					row = x['rows'][isrc]
					cell = row['elements'][idst]
					if cell['status'] == 'OK':
						print('{} to {}: {}, {}.'.format(src, dst, cell['distance']['text'], cell['duration']['text']))
					else:
						print('{} to {}: status = {}'.format(src, dst, cell['status']))

			# Of course, we could have also saved the results in a file,
			with open('gdmpydemo.json', 'w') as f:
				f.write(r.text)

			# TODO Or in a database,

			# Or whatever.
			# ???
			# Profit!

		except ValueError:
			print 'Error while parsing JSON response, program terminated.'

	# Prepare for debugging, but only if interactive. Now you can pprint(x), for example.
	if sys.flags.interactive:
    		from pprint import pprint

