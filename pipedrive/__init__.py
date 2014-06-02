# -*- coding: utf-8 -*-

from httplib2 import Http
import six
from six.moves.urllib.parse import urlencode
import json
from copy import copy

PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1/"

class PipedriveError(Exception):
	def __init__(self, response):
		self.response = response
	def __str__(self):
		return self.response.get('error', 'No error provided')

class IncorrectLoginError(PipedriveError):
	pass

class Pipedrive(object):
	
	def _request(self, endpoint, data, method="POST"):
		
		if self.api_token:
			data = copy(data)
			data['api_token'] = self.api_token
		
		if method in ["DELETE", "PUT", "POST"]:
			if 'id' not in data and method != 'POST':
				raise PipedriveError("No 'id' field, all updates require one.")
			request_url = "%s%s%s?api_token=%s" % (
				PIPEDRIVE_API_URL,
				endpoint,
				str('/%d' % data['id']) if 'id' in data else '',
				data['api_token'],
				)
			del data['api_token']
			request_body = json.dumps(data)
			print('ru: %s' % request_url)
			print('rb: %s' % request_body)
			response, data = self.http.request(request_url, method=method, body=request_body, headers={'Content-Type': 'application/json'})
		else:
                    if 'id' not in data:
                        response, data = self.http.request("%s%s?%s" % (PIPEDRIVE_API_URL, endpoint, urlencode(data)), method)
                    else:
                        response, data = self.http.request("%s%s/%s?%s" % (PIPEDRIVE_API_URL, endpoint, data['id'], urlencode(data)), method)

		return json.loads(six.text_type(data, encoding='utf-8'))

	def __init__(self, login = None, password = None):
		self.http = Http()
		if password:
			response = self._request("/auth/login", {"login": login, "password": password})

			if 'error' in response:
				raise IncorrectLoginError(response)
			
			self.api_token = response['authorization'][0]['api_token']
		else:
			# Assume that login is actually the api token
			self.api_token = login

	def __getattr__(self, name):
		def wrapper(data):
			if 'method' in data: 
				method = data['method'] 
				del data['method']
			else: 
				method = "POST"
			response = self._request(name, data, method)
			if 'error' in response:
				raise PipedriveError(response)
			return response
		return wrapper
