# Environment preparer
* Docker compose will probably go out the window
* Can just make an environment preparer that takes in some image tags and db locations, and set up a network

* I'm thinking I should only bother with supporting docker for simplicity
* For integration testing, use testcontainers to boot up the dependent apps

# Problems I need to solve:
* Inter-app communication -> (REST using docker DNS?)
* Authentication -> (Make apps not require sign up, give agents a JWT they can pass -- just contains their email/name/etc.)
* Database generation -> (Just have a bunch of agents call a bunch of tools?)
* Task generation (selecting valid users to complete the task -> (Manual?)