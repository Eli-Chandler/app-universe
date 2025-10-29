# Environment preparer
* Docker compose will probably go out the window
* Can just make an environment preparer that takes in some image tags and db locations, and set up a network

* I'm thinking I should only bother with supporting docker for simplicity
* For integration testing, use testcontainers to boot up the dependent apps

# Problems I need to solve:
* Inter-app communication -> (REST using docker DNS?)
* Authentication -> (Make apps not require sign up, give agents a JWT they can pass -- just contains their email/name/etc.)
  * We use a JWT, because e.g. if we just used base64, the agent could figure this out and hack someone elses account
* Database generation -> (Just have a bunch of agents call a bunch of tools?)
* Task generation (selecting valid users to complete the task -> (Manual?)


Data generation approach:
Have a generic json file that maps our the core entities, such as people, relationships, companies, etc.
Db generators can pick and choose what they need from this along with synthesizing any extra data they need.