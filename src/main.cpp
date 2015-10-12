#include <onion.hpp>
#include <url.hpp>

int main() {
	Onion::Onion server(O_POOL);

	Onion::Url root(&server);
	root.add("", "static text response", HTTP_OK);
	server.setPort(9999);
	server.setHostname("192.168.1.11");
	server.listen();

	return 0;
}