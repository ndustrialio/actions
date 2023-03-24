#!/usr/bin/env -S node --no-warnings

const main = async (env = "") => {
    console.log('[{"slug":"melting","legacyId":"c5517437-8497-400a-8c6d-a9de88669c70"}]');
    return
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

main(process.argv[1]);

