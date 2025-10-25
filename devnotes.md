# Environment preparer
* Docker compose will probably go out the window
* Can just make an environment preparer that takes in some image tags and db locations, and set up a network

* I'm thinking I should only bother with supporting docker for simplicity
* For integration testing, use testcontainers to boot up the dependent apps
