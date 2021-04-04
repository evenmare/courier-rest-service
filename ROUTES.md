## ROUTES
1. `POST /couriers`
    - *input format*: 
    ```
      {
        'data': [ 
                  {
                    'courier_id': courier_id,                                |  format: unique int
                    'courier_type': type,                                    |  format: string of value 'foot'/'bike'/'car'
                    'regions': regions_list,                                 |  format: list of int
                    'working_hours': [start, end],                           |  format: HH:MM
                  }, 
                    ... ]
      }
    ```
    - **201** output format:
    ```
    {
      'CourierIds: [ list of ids ]
    }
    ```
    
    - **400** output format:
    ```
     {
      'CourierIds: [ list of ids ],
      'error': {
                  'status': 400,
                  'description': 'bad request'/'check by id',
                  'problem_ids': { courier_id: 'incorrect data format' }     |  description 'check by id' required  
                  
                  
    }
    ```
 2. `GET /couriers/{courier_id}`
    - **200** output format:
    ```
    {
         'courier_id': courier_id,                                           |  format: unique int
         'courier_type': type,                                               |  format: string of value 'foot'/'bike'/'car'
         'regions': regions_list,                                            |  format: list of int
         'working_hours': [start, end],                                      |  format: ['HH:MM', 'HH:MM']
         'rating': rating,                                                   |  format: float
         'earnings': earnings                                                |  format: int
    }
    ```
    - **404** output format:
    ```
    {
         'error': 
                  {'status': 404,
                   'description': 'courier not found'}
    }
    ```
 3. `PATCH /couriers/{courier_id}`
    - *input_format*:
    ```
    {
         'courier_type': type,                                               |  format: string of value 'foot'/'bike'/'car'
         'regions': regions_list,                                            |  format: list of int
         'working_hours': [start, end]                                       |  format: ['HH:MM', 'HH:MM']
    }
    ```
    - **200** output format:
    ```
     {
         'courier_id': courier_id,                                           |  format: unique int
         'courier_type': type,                                               |  format: string of value 'foot'/'bike'/'car'
         'regions': regions_list,                                            |  format: list of int
         'working_hours': [start, end],                                      |  format: ['HH:MM', 'HH:MM']
         'rating': rating,                                                   |  format: float
         'earnings': earnings                                                |  format: int
    }
    ```
    - **400** output format:
    ```
    {
      'error': {
                  'status': 400,
                  'description': 'bad request'/'check by id'   
               }
    }
    ```
    - **404** output format:
    ```
    {
         'error': 
                  {'status': 404,
                   'description': 'courier not found'}
    }
    ```
 4. `POST /orders`
    - *input format*: 
    ```
      {
        'data': [ 
                  {
                    'order_id': order_id,                                    | format: unique int
                    'weight': weight,                                        | format: float
                    'region': region,                                        | format: int
                    'delivery_hours': [start, end]                           | format: ['yy-mm-ddTHH:MM:SS.sssZ', 'yyyy-mm-ddTHH:MM:SS.sssZ']
                  },
                    ... ]
     }
     ```
     - **201** output format:
     ```
     {
      'OrderIds: [ list of ids ]
     }
     ```
     - **400** output format:
     ```
     {
       'OrderIds: [ list of ids ],
       'error': {
                   'status': 400,
                   'description': 'bad request'/'check by id',
                   'problem_ids': { order_id: 'incorrect data format' }       |  description 'check by id' required  
                }   
     }
     ```
 5. `POST /orders/assign`
    - *input format*: 
    ```
    {
       'courier_id': courier_id
    }
    ```
    - **200** output format:
    ```
    {
       order_id: assigned_time                                                | filter on output order_ids: assigned courier = courier in request, showing only non-completed orders
    }
    ```
    - **400** output format:
    ```
    {
      'error': {
                  'status': 400,
                  'description': 'bad request' 
               }
    }
    ```
  6. `/orders/complete`
     - *input format*:
     ```
     {
       'courier_id': courier_id,
       'order_id': order_id,
       'complete_time': complete_time                                          | format: 'yy-mm-ddTHH:MM:SS.sssZ'
     }
     ```
     - **200** output format:
     ```
     {
       'order_id': order_id
     }
     ```
     - **400** output format:
     ```
     {
       'error': {
                   'status': 400,
                   'description': 'bad request' 
                }
     }
     ```
