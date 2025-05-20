Necesito crear un MCP server que combine la extracción de datos desde Pitágoras con capacidades de análisis de datos en python. El objetivo es permitir a los usuarios extraer datos de marketing digital y analizarlos directamente en Claude Desktop, ejecutando scripts de Python.

## Instrucciones Técnicas
Escribe el código del MCP server en Python, siguiendo estas directrices:

1) ESTRUCTURA DEL CÓDIGO:
   - Separa los scripts en una estructura modular y clara
   - Utiliza herramientas como pandas, numpy, scipy y sklearn para análisis de datos
   - Almacena las credenciales en un archivo .env con AUTH_TOKEN (sin el prefijo bearer)

2) HERRAMIENTAS:
   - extract_clients_data: Extraer los clientes disponibles para un correo electrónico.
   - mediums_and_accounts_selector: Herramienta para seleccionar los medios y cuentas de los que se va a extraer datos
   - extract_google_ads_data: Extracción de datos de Google Ads
   - extract_facebook_ads_data: Extracción de datos de Facebook Ads
   - extract_google_analytics_data: Extracción de datos de Google Analytics4
   - get_google_ads_metadata: Extracción los campos disponibles para google ads
   - get_facebook_ads_metadata: Extracción los campos disponibles para facebook ads
   - get_google_analytics_metadata: Extracción los campos disponibles para google analytics
   - run_script: Ejecuta scripts, para análisis de datos en Python

3) PROMPTS:
   - Prompt para análisis exploratorio básico de datos de marketing
   - Prompt para comparación de rendimiento entre plataformas 
   - Prompt para recomendaciones de optimización de campañas
   - Garantizar que los prompts usen el sistema run_script para ejecutar el análisis en Python

4) FLUJO DE USUARIO PARA EXTRACCIÓN DE DATOS:
   - Paso 1: Selección del cliente desde una lista
   - Paso 2: Selección del medio publicitario
   - Paso 3: Selección de cuentas específicas (no extraer automáticamente todas)
   - Paso 4: Definición de métricas, dimensiones y fechas

   
5) CONSIDERACIONES DE SEGURIDAD Y RENDIMIENTO:
   - Validar todas las entradas del usuario
   - Implementar manejo de errores para todas las llamadas API
   - Evitar usar bucles for cuando sea posible para optimizar rendimiento

## Pitágoras API endopoints
Te comparto los endpoints, con los body y la respuestas de la API ayúdame con la implementación. (las respuestas están truncadas para evitar gastar tokens), todas las peticiones son tipo POST excepto por Facebook Ads Metadata y Google Ads Metadata que son GET.

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
                    "businessUnit": "Coppel Ecommerce",****
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
    "accounts": [{"name":"Coppel Omnicanal","account_id":"406656800494680"}],
    "fields": [
        "campaign_name",
        "date_start",
        "spend",
        "impressions",
        "clicks"
    ],
    "start_date": "2025-01-01",
    "end_date": "2025-01-02"
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

### Google Analytics Metadata
#### Endpoint: https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/analytics4/metadata
#### Body 
{
    "property_id" : "0",
    "credential_email" : "analytics@epa.digital"
}
#### Response:
{
    "dimensions": [
        {
            "value": "achievementId",
            "label": "Achievement ID"
        },
        {
            "value": "adFormat",
            "label": "Ad format"
        }
    ],
    "metrics": [
        {
            "value": "active1DayUsers",
            "label": "1-day active users"
        },
        {
            "value": "active28DayUsers",
            "label": "28-day active users"
        }
    ]
}
### Facebook Ads Metadata
#### Endpoint: GET https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/facebook/schema
#### Response
{
    "fields": [
        {
            "name": "account_currency",
            "type": "string"
        },
        {
            "name": "account_id",
            "type": "numeric string"
        },
        {
            "name": "account_name",
            "type": "string"
        },
        {
            "name": "ad_click_mobile_app"
        }
    ]
}

### Google ads Metadata
#### Endpoint: GET https://pitagoras-api-l6dmrzkz7a-uc.a.run.app/api/v1/adwords/metrics?resource_name=campaign
#### Response
[
    "metrics.absolute_top_impression_percentage",
    "metrics.clicks",
    "metrics.conversions",
    "metrics.cost_micros",
    "metrics.impressions"
]