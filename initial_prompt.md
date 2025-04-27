# Pitagoras MCP server

## Instrucciones
Escribe el código del MCP server, usa las mejores prácticas de programación en Python, separa los scripts en una estructura clara y conveniente para no tener todo en un solo script, el token de Pitágoras esta en un .env como AUTH_TOKEN. El flow para el cliente del MCP sera que primero que el usuario seleccione el cliente, luego los medios y por último las cuentas de las que requiere extraer los datos.
- El token no debe contener bearer.
- Vamos a mantener la implementación muy simple, el objetivo es lograr obtener datos, posteriormente haremos transformaciones adicionales.
- La mayor parte de la lógica de como solicitar datos a cada medio la vamos a meter en los prompts (Prompts are reusable templates that help LLMs interact with your server effectively) para dejar la lógica de extracción de datos muy simple.
- Implementa las mejores prácticas de programación, evita usar for lops e implementa logs para saber como se construye la petición a Pitágoras y el resultado que regresa.

## Contexto
Trabajo en una agencia de marketing digital especializada en optimizar campañas de paid media.
Pitágoras que es un herramienta interna de extracción de datos de los medios (Google Ads, facebook Ads y Google Analytics) que permite acceder a los datos de las plataformas desde un sidebar en google sheets (Es similar a supermetrics) vamos a consumir su API para crear el MCP para que los usuarios puedan tener sus datos directo en Cloud Desktop. Esta API es muy flexible y nos deja acceder a los datos de las plataformas si tener que hacer transformación de los datos y no tenemos que lidiar con la autentificación.

## Pitágoras API endopoints
Te comparto los endpoints, con los body y la respuestas de la API ayúdame con la implementación. (las respuestas están truncadas)

### Clients

#### Endpoint
https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/customers


#### Body
{
    "user_email": "jcorona@epa.digital"
}

#### Respuesta
{
    "customers": [
        {
            "ID": "0MzvbWaTrW7gedBvdwOD",
            "name": "Coppel Ecommerce",
            "accounts": [
                {
                    "accountID": "1019423192",
                    "businessUnit": "Coppel Ecommerce",
                    "clientName": "Coppel Ecommerce",
                    "credentialEmail": "analytics@epa.digital",
                    "currency": "MXN",
                    "externalLoginCustomerID": "2465423267",
                    "manager": {
                        "name": "Alejandra Rodriguez Herrera",
                        "userID": "GGDAC2AxdOOaTSZ2062JSaHxzNO2"
                    },
                    "name": "Coppel Tienda Shopping",
                    "objective": "ECOMMERCE",
                    "postgresID": 303,
                    "provider": "adwords",
                    "timezone": "America/Mexico_City",
                    "vertical": "Retail"
                },
                {
                    "accountID": "2535179120",
                    "businessUnit": "Coppel Ecommerce",
                    "clientName": "Coppel Ecommerce",
                    "credentialEmail": "analytics@epa.digital",
                    "currency": "MXN",
                    "externalLoginCustomerID": "2465423267",
                    "manager": {
                        "name": "Alejandra Rodriguez Herrera",
                        "userID": "GGDAC2AxdOOaTSZ2062JSaHxzNO2"
                    },
                    "name": "Tienda Coppel",
                    "objective": "ECOMMERCE",
                    "postgresID": 302,
                    "provider": "adwords",
                    "timezone": "America/Mexico_City",
                    "vertical": "Retail"
                },
                {
                    "accountID": "4766471111",
                    "businessUnit": "Coppel Ecommerce",
                    "clientName": "Coppel Ecommerce",
                    "credentialEmail": "analytics@epa.digital",
                    "currency": "MXN",
                    "externalLoginCustomerID": "2465423267",
                    "manager": {
                        "name": "Alejandra Rodriguez Herrera",
                        "userID": "GGDAC2AxdOOaTSZ2062JSaHxzNO2"
                    },
                    "name": "Coppel Tienda Display",
                    "objective": "ECOMMERCE",
                    "postgresID": 304,
                    "provider": "adwords",
                    "timezone": "America/Mexico_City",
                    "vertical": "Retail"
                }          
                ],
            "status": "Activo",
            "postgresID": 0
        }
    ],
    "token": ""
}

### Google Ads

#### Endpoint
https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/adwords/report

#### Body
{
    "accounts": [
        {
            "account_id":"2535179120",
            "name": "Tienda Coppel",
            "login_customer_id": "2465423267"
        },
        {
            "account_id": "7245183205",
            "name":"Coppel Shopping Omnicanal",
            "login_customer_id": "5922771004"
        }
    ],
    "attributes": [
        {
            "resource_name": "campaign",
            "fields": ["campaign.name","campaign.id"]
        }
    ],
    "segments": ["segments.date"],
    "metrics" : ["metrics.cost_micros",
        "metrics.impressions",
        "metrics.clicks"],
    "resource": "campaign",
    "start_date": "2025-01-01",
    "end_date": "2025-01-01"
}

#### Respuesta
{
    "headers": [
        "campaign.name",
        "campaign.id",
        "segments.date",
        "metrics.cost_micros",
        "metrics.impressions",
        "metrics.clicks"
    ],
    "rows": [
        [
            "aw_coppel_tnd_do_pmax_cat_motos_y_automotriz",
            "17570740212",
            "2025-01-01",
            "12201.452817",
            "527820",
            "9144"
        ],
        [
            "aw_coppel_tnd_do_pmax_cat_hogar_y_muebles",
            "17570794986",
            "2025-01-01",
            "35517.145955",
            "1670656",
            "37293"
        ]
    ],
    "errors": []
}

### Facebook Ads

#### Endpoint
https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/facebook/report

#### Body
{
    "provider": "fb",
    "preset_date": {
        "range": "last45Days",
        "days": 45
    },
    "customer": "0MzvbWaTrW7gedBvdwOD",
    "query_name": "data_fb",
    "parsed_accounts": [
        {
            "name": "Coppel Omnicanal",
            "account_id": "406656800494680"
        }
    ],
    "accounts": [
        "406656800494680"
    ],
    "date_range": {
        "end": "2024-05-11",
        "start": "2022-11-21"
    },
    "fields": [
        "campaign_name",
        "date_start",
        "spend",
        "impressions",
        "clicks"
    ]
}

#### Respuesta
{
    "headers": [
        "campaign_name",
        "date_start",
        "spend",
        "impressions",
        "clicks"
    ],
    "rows": [
        [
            "fb_coppel_tnd_do_auct_dpa_cart_2024",
            "2025-01-01",
            "655019",
            "11029306",
            "338234"
        ],
        [
            "fb_coppel_tnd_do_auct_daba_pm_value_2024",
            "2025-01-01",
            "147948",
            "6965578",
            "237255"
        ]
    ],
    "errors": []
}

### Google Analytics

#### Endpoint
https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/analytics4/report

#### Body
{
    "accounts": [
        {
            "property_id": "196407566",
            "name": "Chedraui",
            "credential_email": "analytics@epa.digital"
        }
    ],
    "dimensions": [
        "date",
        "sessionCampaignName",
        "sessionSourceMedium"
    ],
    "metrics": [
        "sessions",
        "transactions",
        "totalRevenue"
    ],
    "start_date": "2025-04-01",
    "end_date": "2025-04-07",
    "filters": {
        "or": [
            {
                "in": [
                    "aw_",
                    {
                        "var": "sessionCampaignName"
                    }
                ]
            },
            {
                "in": [
                    "fb_",
                    {
                        "var": "sessionCampaignName"
                    }
                ]
            }
        ]
    }
}

#### Respuesta
{
    "headers": [
        "date",
        "sessionCampaignName",
        "sessionSourceMedium",
        "sessions",
        "transactions",
        "totalRevenue"
    ],
    "rows": [
        [
            "2025-04-02",
            "aw_chedraui_branding_middle_think_demand_gen_aon",
            "google / cpc",
            "111704",
            "19",
            "11819.380027"
        ],
        [
            "2025-04-02",
            "fb_chedraui_branding_middle_think_auct_conv_view_content",
            "facebook / cpc",
            "111524",
            "5",
            "8642.000004"
        ]
    ],
    "errors": []
}