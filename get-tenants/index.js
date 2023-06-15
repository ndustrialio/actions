#!/usr/bin/env -S node --no-warnings

const main = async (env = "") => {
    env = "staging" //TODO remove when prod works
    const url = `https://nio-internal.api${env == 'prod'? "" : ".staging"}.ndustrial.io/graphql`;

    const response = await fetch(url, {
          "headers": {
            "content-type": "application/json",
          },
          "body": JSON.stringify({
            query: `{
            tenants(filter: { nionicEnabled: { equalTo: true }}) {
              nodes {
                slug
                legacyId
              }
            }
          }`}),
          "method": "POST"
        });
    const tenants = await response.json();
    console.log(JSON.stringify(tenants.data.tenants.nodes));
}

main(process.argv[2]);

