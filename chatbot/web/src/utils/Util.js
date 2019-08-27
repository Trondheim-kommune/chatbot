export async function fetchData(url, method, body) {
  const response = await fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(body),
  });
  return await response.json();
}

export async function fetchDataWithoutTypeHeader(url, method) {
  const response = await fetch(url, {
    method: method,
	  headers: {
		  Accept: 'application/json',
		}
	});
	return await response.json();
}
