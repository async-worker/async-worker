Search.setIndex({docnames:["changelog/index","changelog/v0.10.0","changelog/v0.10.1","changelog/v0.11.0","changelog/v0.11.1","changelog/v0.11.2","devguide/index","devguide/tests","incompat","index","intro","src/asyncworker/asyncworker","src/asyncworker/asyncworker.connections","src/asyncworker/asyncworker.easyqueue","src/asyncworker/asyncworker.exceptions","src/asyncworker/asyncworker.rabbitmq","src/asyncworker/asyncworker.signals","src/asyncworker/asyncworker.signals.handlers","src/asyncworker/asyncworker.sse","src/asyncworker/asyncworker.testing","src/asyncworker/asyncworker.types","src/asyncworker/modules","userguide/asyncworker-app/hooks","userguide/asyncworker-app/index","userguide/asyncworker-app/intro","userguide/asyncworker-app/storage","userguide/handlers/http","userguide/handlers/index","userguide/handlers/rabbitmq","userguide/index","userguide/quickstart","userguide/updates/index","userguide/utils/index","userguide/utils/run_every","userguide/utils/timeit"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["changelog/index.rst","changelog/v0.10.0.rst","changelog/v0.10.1.rst","changelog/v0.11.0.rst","changelog/v0.11.1.rst","changelog/v0.11.2.rst","devguide/index.rst","devguide/tests.rst","incompat.rst","index.rst","intro.rst","src/asyncworker/asyncworker.rst","src/asyncworker/asyncworker.connections.rst","src/asyncworker/asyncworker.easyqueue.rst","src/asyncworker/asyncworker.exceptions.rst","src/asyncworker/asyncworker.rabbitmq.rst","src/asyncworker/asyncworker.signals.rst","src/asyncworker/asyncworker.signals.handlers.rst","src/asyncworker/asyncworker.sse.rst","src/asyncworker/asyncworker.testing.rst","src/asyncworker/asyncworker.types.rst","src/asyncworker/modules.rst","userguide/asyncworker-app/hooks.rst","userguide/asyncworker-app/index.rst","userguide/asyncworker-app/intro.rst","userguide/asyncworker-app/storage.rst","userguide/handlers/http.rst","userguide/handlers/index.rst","userguide/handlers/rabbitmq.rst","userguide/index.rst","userguide/quickstart.rst","userguide/updates/index.rst","userguide/utils/index.rst","userguide/utils/run_every.rst","userguide/utils/timeit.rst"],objects:{"":{asyncworker:[11,0,0,"-"]},"asyncworker.app":{App:[11,1,1,""]},"asyncworker.app.App":{freeze:[11,2,1,""],get_connection:[11,2,1,""],get_connection_for_route:[11,2,1,""],handlers:[11,3,1,""],route:[11,2,1,""],run:[11,2,1,""],run_every:[11,2,1,""],run_on_shutdown:[11,2,1,""],run_on_startup:[11,2,1,""],shutdown:[11,2,1,""],shutdown_os_signals:[11,3,1,""],startup:[11,2,1,""]},"asyncworker.bucket":{Bucket:[11,1,1,""],BucketFullException:[11,4,1,""]},"asyncworker.bucket.Bucket":{is_empty:[11,2,1,""],is_full:[11,2,1,""],pop_all:[11,2,1,""],put:[11,2,1,""],used:[11,2,1,""]},"asyncworker.conf":{Settings:[11,1,1,""]},"asyncworker.conf.Settings":{Config:[11,1,1,""]},"asyncworker.conf.Settings.Config":{allow_mutation:[11,3,1,""],env_prefix:[11,3,1,""]},"asyncworker.connections":{AMQPConnection:[11,1,1,""],Connection:[11,1,1,""],ConnectionsMapping:[11,1,1,""],SSEConnection:[11,1,1,""]},"asyncworker.connections.AMQPConnection":{Config:[11,1,1,""],items:[11,2,1,""],keys:[11,2,1,""],put:[11,2,1,""],register:[11,2,1,""],set_connections:[11,2,1,""],values:[11,2,1,""]},"asyncworker.connections.AMQPConnection.Config":{arbitrary_types_allowed:[11,3,1,""]},"asyncworker.connections.ConnectionsMapping":{add:[11,2,1,""],with_type:[11,2,1,""]},"asyncworker.consumer":{Consumer:[11,1,1,""]},"asyncworker.consumer.Consumer":{consume_all_queues:[11,2,1,""],keep_runnig:[11,2,1,""],on_before_start_consumption:[11,2,1,""],on_connection_error:[11,2,1,""],on_consumption_start:[11,2,1,""],on_message_handle_error:[11,2,1,""],on_queue_error:[11,2,1,""],on_queue_message:[11,2,1,""],queue_name:[11,2,1,""],start:[11,2,1,""]},"asyncworker.easyqueue":{connection:[13,0,0,"-"],exceptions:[13,0,0,"-"],message:[13,0,0,"-"],queue:[13,0,0,"-"]},"asyncworker.easyqueue.connection":{AMQPConnection:[13,1,1,""]},"asyncworker.easyqueue.connection.AMQPConnection":{close:[13,2,1,""],connection_parameters:[13,2,1,""],is_connected:[13,2,1,""]},"asyncworker.easyqueue.exceptions":{EmptyQueueException:[13,4,1,""],InvalidMessageSizeException:[13,4,1,""],MessageError:[13,4,1,""],UndecodableMessageException:[13,4,1,""]},"asyncworker.easyqueue.message":{AMQPMessage:[13,1,1,""]},"asyncworker.easyqueue.message.AMQPMessage":{ack:[13,2,1,""],channel:[13,3,1,""],connection:[13,3,1,""],delivery_tag:[13,3,1,""],deserialized_data:[13,2,1,""],queue_name:[13,3,1,""],reject:[13,2,1,""],serialized_data:[13,3,1,""]},"asyncworker.easyqueue.queue":{BaseJsonQueue:[13,1,1,""],BaseQueue:[13,1,1,""],DeliveryModes:[13,1,1,""],JsonQueue:[13,1,1,""],QueueConsumerDelegate:[13,1,1,""]},"asyncworker.easyqueue.queue.BaseJsonQueue":{content_type:[13,3,1,""],deserialize:[13,2,1,""],serialize:[13,2,1,""]},"asyncworker.easyqueue.queue.BaseQueue":{deserialize:[13,2,1,""],serialize:[13,2,1,""]},"asyncworker.easyqueue.queue.DeliveryModes":{NON_PERSISTENT:[13,3,1,""],PERSISTENT:[13,3,1,""]},"asyncworker.easyqueue.queue.JsonQueue":{consume:[13,2,1,""],deserialize:[13,2,1,""],put:[13,2,1,""],serialize:[13,2,1,""],stop_consumer:[13,2,1,""]},"asyncworker.easyqueue.queue.QueueConsumerDelegate":{on_before_start_consumption:[13,2,1,""],on_connection_error:[13,2,1,""],on_consumption_start:[13,2,1,""],on_message_handle_error:[13,2,1,""],on_queue_message:[13,2,1,""]},"asyncworker.exceptions":{InvalidConnection:[11,4,1,""],InvalidRoute:[11,4,1,""]},"asyncworker.options":{Actions:[11,1,1,""],AutoNameEnum:[11,1,1,""],DefaultValues:[11,1,1,""],Events:[11,1,1,""],Options:[11,1,1,""],RouteTypes:[11,1,1,""]},"asyncworker.options.Actions":{ACK:[11,3,1,""],REJECT:[11,3,1,""],REQUEUE:[11,3,1,""]},"asyncworker.options.DefaultValues":{BULK_FLUSH_INTERVAL:[11,3,1,""],BULK_SIZE:[11,3,1,""],ON_EXCEPTION:[11,3,1,""],ON_SUCCESS:[11,3,1,""],RUN_EVERY_MAX_CONCURRENCY:[11,3,1,""]},"asyncworker.options.Events":{ON_EXCEPTION:[11,3,1,""],ON_SUCCESS:[11,3,1,""]},"asyncworker.options.Options":{BULK_FLUSH_INTERVAL:[11,3,1,""],BULK_SIZE:[11,3,1,""],MAX_CONCURRENCY:[11,3,1,""]},"asyncworker.options.RouteTypes":{AMQP_RABBITMQ:[11,3,1,""],HTTP:[11,3,1,""],SSE:[11,3,1,""]},"asyncworker.rabbitmq":{message:[15,0,0,"-"]},"asyncworker.rabbitmq.message":{RabbitMQMessage:[15,1,1,""]},"asyncworker.rabbitmq.message.RabbitMQMessage":{accept:[15,2,1,""],body:[15,2,1,""],process_exception:[15,2,1,""],process_success:[15,2,1,""],reject:[15,2,1,""],serialized_data:[15,2,1,""]},"asyncworker.routes":{AMQPRoute:[11,1,1,""],HTTPRoute:[11,1,1,""],Model:[11,1,1,""],Route:[11,1,1,""],RoutesRegistry:[11,1,1,""],SSERoute:[11,1,1,""],call_http_handler:[11,5,1,""],http_handler_wrapper:[11,5,1,""]},"asyncworker.routes.HTTPRoute":{aiohttp_routes:[11,2,1,""],validate_method:[11,2,1,""]},"asyncworker.routes.Model":{get:[11,2,1,""],keys:[11,2,1,""]},"asyncworker.routes.Route":{factory:[11,2,1,""]},"asyncworker.routes.RoutesRegistry":{add_route:[11,2,1,""],amqp_routes:[11,3,1,""],http_routes:[11,3,1,""],route_for:[11,2,1,""],sse_routes:[11,3,1,""]},"asyncworker.routes.SSERoute":{add_default_headers:[11,2,1,""]},"asyncworker.signals":{base:[16,0,0,"-"],handlers:[17,0,0,"-"]},"asyncworker.signals.base":{Freezable:[16,1,1,""],Signal:[16,1,1,""]},"asyncworker.signals.base.Freezable":{freeze:[16,2,1,""],frozen:[16,2,1,""]},"asyncworker.signals.base.Signal":{send:[16,2,1,""]},"asyncworker.signals.handlers":{base:[17,0,0,"-"],http:[17,0,0,"-"],rabbitmq:[17,0,0,"-"],sse:[17,0,0,"-"]},"asyncworker.signals.handlers.base":{SignalHandler:[17,1,1,""]},"asyncworker.signals.handlers.base.SignalHandler":{shutdown:[17,2,1,""],startup:[17,2,1,""]},"asyncworker.signals.handlers.http":{HTTPServer:[17,1,1,""]},"asyncworker.signals.handlers.http.HTTPServer":{shutdown:[17,2,1,""],startup:[17,2,1,""]},"asyncworker.signals.handlers.rabbitmq":{RabbitMQ:[17,1,1,""]},"asyncworker.signals.handlers.rabbitmq.RabbitMQ":{startup:[17,2,1,""]},"asyncworker.signals.handlers.sse":{SSE:[17,1,1,""]},"asyncworker.signals.handlers.sse.SSE":{startup:[17,2,1,""]},"asyncworker.sse":{consumer:[18,0,0,"-"],message:[18,0,0,"-"]},"asyncworker.sse.consumer":{SSEConsumer:[18,1,1,""],State:[18,1,1,""]},"asyncworker.sse.consumer.SSEConsumer":{interval:[18,3,1,""],keep_runnig:[18,2,1,""],on_connection:[18,2,1,""],on_connection_error:[18,2,1,""],on_event:[18,2,1,""],on_exception:[18,2,1,""],start:[18,2,1,""]},"asyncworker.sse.consumer.State":{EVENT_DATA_FOUND:[18,3,1,""],EVENT_NAME_FOUND:[18,3,1,""],WAIT_FOR_DATA:[18,3,1,""]},"asyncworker.sse.message":{SSEMessage:[18,1,1,""]},"asyncworker.task_runners":{ScheduledTaskRunner:[11,1,1,""]},"asyncworker.task_runners.ScheduledTaskRunner":{can_dispatch_task:[11,2,1,""],start:[11,2,1,""],stop:[11,2,1,""]},"asyncworker.testing":{HttpClientContext:[11,1,1,""],http_client:[11,5,1,""]},"asyncworker.time":{ClockTicker:[11,1,1,""]},"asyncworker.time.ClockTicker":{stop:[11,2,1,""]},"asyncworker.types":{registry:[20,0,0,"-"],resolver:[20,0,0,"-"]},"asyncworker.types.registry":{TypesRegistry:[20,1,1,""]},"asyncworker.types.registry.TypesRegistry":{get:[20,2,1,""],set:[20,2,1,""]},"asyncworker.types.resolver":{ArgResolver:[20,1,1,""],MissingTypeAnnotationError:[20,4,1,""]},"asyncworker.types.resolver.ArgResolver":{resolve_param:[20,2,1,""],wrap:[20,2,1,""]},"asyncworker.utils":{Timeit:[11,1,1,""],entrypoint:[11,5,1,""]},"asyncworker.utils.Timeit":{TRANSACTIONS_KEY:[11,3,1,""]},asyncworker:{app:[11,0,0,"-"],bucket:[11,0,0,"-"],conf:[11,0,0,"-"],connections:[11,0,0,"-"],consumer:[11,0,0,"-"],easyqueue:[13,0,0,"-"],exceptions:[11,0,0,"-"],options:[11,0,0,"-"],rabbitmq:[15,0,0,"-"],routes:[11,0,0,"-"],signals:[16,0,0,"-"],sse:[18,0,0,"-"],task_runners:[11,0,0,"-"],testing:[11,0,0,"-"],time:[11,0,0,"-"],types:[20,0,0,"-"],utils:[11,0,0,"-"]}},objnames:{"0":["py","module","Python m\u00f3dulo"],"1":["py","class","Python classe"],"2":["py","method","Python m\u00e9todo"],"3":["py","attribute","Python atributo"],"4":["py","exception","Python exce\u00e7\u00e3o"],"5":["py","function","Python fun\u00e7\u00e3o"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:exception","5":"py:function"},terms:{"0994415283203125e":34,"0x10c10c7c8":34,"S\u00e3o":24,"Tamb\u00e9m":34,"\u00edndic":9,"\u00fanic":25,"a\u00e7\u00e3":29,"abstract":[11,13],"ap\u00f3s":28,"ass\u00edncron":[8,9,22,23,29,34],"atr\u00e1vez":[],"atrav\u00e9s":[26,29],"c\u00f3dig":[8,11,12,13,14,15,16,17,18,19,20,24,25,26,30,34],"c\u00f3p":27,"cen\u00e1ri":22,"ci\u00eanc":26,"class":[7,9,11,12,13,15,16,17,18,19,20,23,28,29,34],"conclu\u00edd":28,"conex\u00e3":[22,28,30],"conex\u00f5":[22,24],"conte\u00fad":31,"cria\u00e7\u00e3":28,"default":[11,28],"descri\u00e7\u00e3":2,"dicion\u00e1ri":[25,28],"din\u00e2m":26,"ent\u00e3":[25,31],"enum":[11,18,24,31],"espec\u00edf":8,"est\u00e3":[24,26,28],"est\u00edmul":[8,9,24,27],"estat\u00e3":28,"exca\u00e7\u00e3":28,"exce\u00e7\u00e3":34,"f\u00f3rmul":28,"far\u00e3":24,"final":34,"float":11,"fun\u00e7\u00e3":[9,26,27,29,32],"fun\u00e7\u00f5":24,"function":26,"import":[22,26,28,30,31,33,34],"in\u00edci":[9,29],"inst\u00e2nc":[24,25,26,28,30,31,34],"int":[11,13,15,28],"intermedi\u00e1ri":26,"ir\u00e1":28,"long":25,"m\u00e1xim":28,"m\u00e3os":[],"m\u00e9tod":[1,24,26,28,31,33],"m\u00e9tric":34,"m\u00f3dul":[9,24,30],"m\u00faltipl":[7,8,24,29,32],"manuten\u00e7\u00e3":25,"n\u00famer":28,"necess\u00e1ri":[24,26,28],"new":[11,12,13],"obrigat\u00f3ri":[24,31],"op\u00e7\u00e3":[],"op\u00e7\u00f5":[24,28],"p\u00e1gin":9,"padr\u00e3":[7,26,28,31],"par\u00e2metr":[11,13,24],"poss\u00edv":24,"poss\u00edvel":[25,26,30,34],"pr\u00e1tic":25,"pr\u00e9v":28,"pr\u00f3pri":[25,26],"public":28,"r\u00e1p":[9,29],"raz\u00e3":26,"requisi\u00e7\u00e3":[9,30],"requisi\u00e7\u00f5":[26,29],"return":[13,26,30],"ser\u00e3":24,"situa\u00e7\u00f5":28,"static":11,"transa\u00e7\u00f5":[29,32],"unit\u00e1ri":[6,9],"usu\u00e1ri":26,"utilit\u00e1ri":[9,29],"utilit\u00e1ti":33,"v\u00e1l":26,"v\u00e1r":[8,9,34],"v\u00eam":31,"vers\u00e3":[4,26,31,34],"with":[3,11,34],Com:28,Como:[22,26,28],Ele:24,Essa:[8,26,28],Essas:[8,9],Esse:[24,26,28,30],Esses:28,Isso:[8,26,27,28],Mais:[],Por:[7,8,9,24,26,27,28],Seu:[],Uma:9,__init__:[],_amqprouteoptions:28,_asynci:11,_handl:28,_hooks_:25,_on_event:30,_type:20,_wrapp:26,abaix:[9,27],abc:[11,12],abert:22,abrim:22,abstracteventloop:13,accept:[15,28],access:34,access_some_remote_content:34,acess:[28,30],ack:[11,13,15,28,30,31],acord:27,actions:[11,15,28],acts:11,add:[11,12],add_default_headers:11,add_rout:11,adiant:26,adicion:[1,7,26,29],age:25,agor:31,aguard:28,aioamqp:13,aiohttp:[11,26,30],aiohttp_rout:11,aiologg:8,aiored:22,algum:[26,28,30],alguns:[27,28],all:[11,12,13,16],allow:[11,12],allow_mutation:11,along:11,also:[11,12],alter:[26,28],ambas:[28,30],ambos:30,amqp:[],amqp_conn:[28,30],amqp_messag:[15,28],amqp_rabbitmq:[11,25,28,30,34],amqp_rout:11,amqpconnection:[11,12,13,29,30],amqpmessag:[11,13,15,28],amqprout:11,ancestral:[11,12],and:[1,11,12,13],anot:33,anoth:28,another_exchang:28,anterior:[8,22],antes:22,antig:31,any:[11,12,13,16,20],apen:[8,27,28,29],aplic:[8,9,22,24,25,29],apllic:[],app:[3,8,9,17,19,21,26,28,29,30,33,34],appid:30,application:[11,13],apps:8,aqu:[7,26,28],arbitrary_types_allowed:[11,12],are:16,argresolv:20,args:16,arguments:[11,13,16],armazen:[23,29],aser:[],asgard:[28,30,31],assim:[22,26,28,30,31],assinatur:[24,26,28,31],assum:30,async:[9,11,12,13,15,16,17,18,22,25,26,28,30,31,33,34],asynci:[11,13,16,34],asynciterator:11,asyncowk:[24,26],asynctest:7,asyncwok:[],asyncwork:[1,8,22,25,26,27,28,29,30,33,34],asyncworker_:11,asyncworker_flush_timeout:28,asyncworker_http_host:26,asyncworker_http_port:26,asynqueu:[11,13],asynwork:30,atend:30,atribut:[7,26,28,31],attr:[],atual:8,atualiz:[4,9,29],aut:[11,12],autentic:26,auth_required:26,authorization:26,automat:[28,30],automatically:11,autonameenum:11,availabl:[11,12],await:[11,22,26,28,34],awaited:11,b2wdigital:9,backend:[],backends:[],banc:22,bas:[11,12,13,14,15,18,19,20,21],baseapp:[],based:16,basejsonqueu:13,basemodel:[11,12],basequeu:13,basesettings:11,basic_auth:26,bast:[7,28,33],befor:[11,13],behav:[11,16],bem:[22,26],bibliotec:22,binding:26,bla:[],boa:25,body:[11,13,15,30,31],bool:11,boot:24,brok:[9,13,28],bucket:[18,21,28],bucket_class:[11,18],bucketfullexception:11,bulk:28,bulk_flush_interval:[11,28],bulk_siz:[11,30],busc:9,bytes:[11,12,13,18],cad:[7,24,27,29,30,31],call:[11,13],call_http_handl:[11,26],callabl:[11,13,34],callback:[11,13,16,34],called:[11,13],can:13,can_dispatch_task:11,cancelling:13,capaz:30,cas:[7,22,28,30,34],caus:[7,8,11,27],caused:11,central:24,certez:7,cham:[24,26,27,28,31,33,34],chang:1,changelog:9,channel:13,chav:28,cheg:27,cicl:[8,22,25],classmethod:[11,12],client:[13,22],clock:11,clocktick:11,clos:[13,22],cod:1,codeowners:1,coerent:2,collections:[11,12,16],comando:30,comec:24,commits:[3,4,5],common:[11,12],compartilh:[9,22,23,29],compat:28,comport:8,comum:22,comunic:28,condition:[11,14],conect:24,conf:21,config:[11,12],configur:31,configurad:[],confirm:[15,28,30],conflit:25,connecions:[],connect:16,connection:[11,12,14,21],connection_parameters:13,connections:[3,21,24,28,30],connectionsmapping:[11,12],connects:13,consegu:28,consig:26,construtor:[24,28],consum:[13,21,29],consume_all_queu:11,consumed:[11,13],consumer_nam:13,consumer_tag:[11,13],consumption:[11,13],cont:[26,34],content:11,content_typ:13,contents:21,context:[29,32],cor:11,coro_ref:20,corotin:26,coroutin:[11,13,16,34],corret:26,count:[11,12],counts:[28,30,31],coverag:1,create_pool:22,cri:[7,8,22,23,27,28,29,31],curl:30,custom:[11,13],customiz:29,dad:[9,22,23,26,29,34],dat:[11,12,13,16,28,30],dcorator:[],deadlock:28,decl:1,declar:[24,28,30],decod:13,decor:26,decorator:[11,12,24,29,32,33],decorators:29,decortor:28,def:[22,25,26,28,30,31,33,34],defaultvalu:[11,28],defin:[11,14,23,28,29],definition:[11,14],del:[26,27],delegat:13,delegate_class:13,delivery_tag:[11,13,15,28],deliverymod:13,dentr:[24,28,34],depend:8,dependenc:2,dependency:1,dependent:24,depist:[],deployment_inf:30,deployment_success:30,depo:[22,31],deposit:24,descart:[15,28],desconect:30,desej:28,desenvolv:9,deserializ:13,deserialization:11,deserialization_method:13,deserialized:[11,13],deserialized_dat:13,dess:[24,26,27,28,31],destin:28,detalh:[9,26,27],dev:[24,26,28],devolv:[28,30,31],diari:28,dict:[11,18,24,28],diferent:[8,9,27,28],diret:26,disponibiliz:25,diss:[26,28],diz:[24,28],doc:[7,26],docs:[1,26],dogs:28,drain_handl:[25,28,30,31,34],durant:8,during:[11,13],each:[11,12],easyqueu:[1,11,12,15,21,28],econtr:9,efet:24,emptyqueueexception:13,encher:28,encontr:26,endpoint:29,entand:26,entend:[8,9,27],entrypoint:11,enumeration:[11,18],env:28,env_prefix:11,env_settings:11,envelop:13,envi:[28,30],envs:29,envvars:26,erro:[1,30],error:[11,34],errors:[28,30,31],erros:[28,30],escolh:[25,29],escrev:[6,8,9,26,28],escrit:28,escut:29,especial:24,esper:28,estad:25,estam:30,estar:[24,29,30],estav:2,estej:8,estimul:26,estiv:28,esvazi:28,etc:[],event:[8,9,11,16,22,27,30],event_body:18,event_data_found:18,event_handl:31,event_nam:[18,30],event_name_found:18,event_raw_body:18,events:[9,11,13,28,29,31],every:[11,13],every_5_seconds:33,evit:[25,28],exc_tb:34,exc_type:34,exc_val:34,exception:[11,13,14,18,20,28,30,31],exceptions:21,exchang:[11,12,13,28],execu:[15,28,34],execut:24,exempl:[22,26,27,30],exist:28,exmepl:24,explicit:34,extern:27,extra:26,extra_registri:20,facilit:[],factory:11,fails:[11,13],fal:[24,30],fals:[11,13,15,28],far:24,fat:8,faz:[7,22,26],featur:1,fech:22,fic:[28,30],fil:[5,15,24,27,28,29,31],fim:[15,22,28],finaliz:22,fiqu:28,fired:16,fix:[9,28,29,32],flask:[],fluentd:[28,30,31],flush_timeout:28,font:[11,12,13,14,15,16,17,18,19,20,24,28],foo:34,form:24,framework:[8,9],freez:[11,16],freezabl:[11,12,16],frent:30,from:[13,22,26,28,30,31,33,34],frozen:16,funcion:9,functools:26,furth:[11,13],futur:11,generat:[11,12],generated:13,generic:[3,11,12,13],ger:[8,9,30],geral:[8,30],gerenc:[29,32],get:[11,13,20,26,30],get_authenticated_us:26,get_connection:11,get_connection_for_rout:11,get_event_loop:34,github:9,given:11,glob:25,guest:[28,30,31],gui:9,handl:[11,15,24,27,28,29,30,31],handled:[11,13],handler_error:[11,13],handlers:[9,11,16,23,25,28,29],handling:[11,13],handnl:[],happens:11,headers:26,heartbeat:13,hell:30,hook:1,hooks:[9,23,29],host:[11,13,28,30,31],hostnam:28,html:26,http:[9,11,16,24,27,29],http_client:[11,19],http_handler_wrapp:11,http_rout:11,httpclientcontext:[11,19],httpm:[],httprout:11,https:[9,26],httpserv:[11,17],httpstatus:26,ide:30,identifi:13,implement:[11,13],implementation:16,inclusiv:25,incompat:8,incompatibil:[7,9],indetermin:[8,9],index:30,indic:[15,28],individual:29,info:31,inform:26,inicializ:[9,22,23,29],init_red:22,initialization:[11,13],injet:25,inner:26,insert:1,insert_user_into_type_registry:[],insid:11,inspir:[],instanc:26,instanced:[11,13],integr:2,inteir:28,interval:[9,11,18,29,32],introdu:9,invalid:[11,14],invalidconnection:[11,14],invalidmessagesizeexception:13,invalidrout:[11,14],is_connected:13,is_empty:11,is_full:11,isn:13,issu:[1,8],item:11,items:[11,12],itens:[],iterabl:[11,12,24],iteration:11,json:[13,30],json_respons:[26,30],jsonqueu:[11,12,13],junt:26,keep_runnig:[11,18],keeping:[11,12],keeps:[11,12],key:[11,13,28],keyerror:34,keys:[11,12],kwarg:1,kwargs:[11,13,16,24,34],lanc:[28,30],latest:[],lembr:25,len:30,lend:29,levant:34,liber:28,licens:5,lik:[11,28],linh:30,list:[11,12,16,18,24,26,27,28,30,31],localhost:22,locks:16,log:30,log_callback:34,logg:[13,31],logging:13,logs:8,loop:[8,11,13,22,30,34],loops:[7,8],los:[25,26],lot:31,main:[11,12,30,34],maior:8,manipul:25,mant:[22,25],mapping:[11,12],marc:[15,28,34],martiusweb:[],max_concurrency:11,max_message_length:13,may:[11,13],melhor:1,menor:28,mensag:[1,9,15,24,27,28,30,31],mensagens:[27,28,30,31],mensg:29,mesm:[24,27,28,30,34],messag:[11,21,25,28,30,31,34],messageerror:[11,13],meth:[],method:16,methods:[1,26,30],microframework:[],min:28,missingtypeannotationerror:20,model:[11,28],models:[26,31],modul:[1,21],moment:[26,28],mostr:[26,30],mov:1,msg:[11,13,28],msgs:28,mud:[2,27,31],muit:[8,34],multipl:3,mutablemapping:11,my_handler_decorator:26,myapp:33,myproject:26,mywork:30,nad:28,nam:[11,12,13,30,34],named:16,nao:1,necess:22,necessari:24,necessit:[22,28],needed:13,nenhum:28,ness:[24,28,30,31,33],nom:[25,28],non:[11,12,13,18,20,24,34],non_persistent:13,noss:24,not:26,notifications:13,nov:[7,8,23,26,27,28,29,34],obj:20,object:[11,12,13,15,16,17,18,19,20,34],objet:[8,9,24,26,28,30,31,33],obs:25,occurred:11,on_before_start_consumption:[11,13],on_connection:18,on_connection_error:[11,13,18],on_consumption_start:[11,13],on_error:13,on_event:18,on_exception:[11,15,18,28],on_excption:[],on_message_handle_error:[11,13],on_queue_error:11,on_queue_messag:[11,13],on_shutdown:22,on_startup:[11,22],on_success:[11,15,28],once:[11,13],onde:[24,28,29],one:13,opcional:28,optional:[11,13,20],options:[12,15,21,24,30],org:26,orig:[24,27],origens:[8,9,24],original:[15,28,31],original_queu:28,orign:8,other:28,outr:[24,28],overwritten:[11,13],owner:16,packag:21,par:[2,4,7,8,9,10,13,15,22,24,25,29,30,31,34],param_typ:20,parametr:[15,24,26,27,29],parametriz:29,part:31,pass:[26,28,31],password:[11,13,18,28,30,31],paths:[24,26],payload:13,peg:[26,28],pel:[8,25,26,28,30],permit:[22,26,33],persistent:[13,22],plan:30,pod:[8,9,24,25,26,27,28,30,31,34],pont:[24,28,30],pop_all:11,popul:26,porqu:27,port:29,posicional:[],position:1,poss:26,possibil:31,possu:28,posu:33,pra:28,prametr:26,precis:[7,22,26,28,30,31],prefetch_count:[11,13,28,30,31],prefretch:28,pres:28,primeir:24,principal:[9,23,26,28,29],print:[28,30,33,34],printit:34,problem:8,process:[22,28],process_exception:15,process_success:15,processed_messag:25,projet:[2,8,10],properti:13,property:[11,13,15,16],provided:13,publish:13,published:13,publishing:13,pud:26,put:[11,12,13,28],pydantic:[2,4,11,12,28],python:[8,9],qenumerator:[],quaisqu:[24,26],qualqu:[8,9],quand:[1,26,27,28,30],queo:[],quer:[28,34],queu:[11,12,21,28,34],queue_nam:[11,13],queueconsumerdelegat:[11,13],rabbit:[],rabbitmq:[9,11,16,21,24,27,29,31],rabbitmqmessag:[11,15,28,31],rabitmq:28,rais:34,raised:[11,13],random:13,raw:[3,4,5,11],readthedocs:[],ready:[11,13],realiz:28,receb:[8,9,24,27,29,31,34],receiv:11,received:30,receivers:16,recoloc:[15,28],recomend:25,reconect:30,recorrent:9,red:22,ref:[],regist:[11,12],registered:16,registers:11,registr:[22,24,27],registry:26,regr:26,reject:[11,13,15,28,30,31],rejeit:[15,28],remov:1,renov:8,reports:1,represent:[22,24,28],req:[26,30],request:[11,24,27,29,30],requeu:[11,13,15,28,30],resolu:26,resolve_p:20,respect:26,respons:[26,30],responsibl:[11,12],retorn:[26,31],returns:[11,12],rod:[2,7,8,9,22,28,29,32],rot:[24,30],rout:[1,14,21,24,25,29,30,31,34],route_for:[1,11],route_inf:[11,18],route_typ:[11,12],routedef:11,routesregistry:[1,11],routetyp:[11,12,24,25,26,28,30,31,34],routing:[13,28],routing_key:[11,12,13,28],run:[11,22,24,30,33],run_every:[11,33],run_every_max_concurrency:11,run_on_shutdown:[11,23,29],run_on_startup:[1,11,23,29],run_until_complet:34,runn:7,running:11,sab:[24,26],schedul:11,scheduledtaskrunn:11,seconds:11,seconds_between_conn_retry:13,seguint:[24,26,28,30],segund:28,sej:[8,24,25,26,28,30,33,34],sempr:[26,28,30],send:[2,7,8,16,26],sending:13,sends:16,ser:[2,8,9,15,22,24,26,27,29,30,31,33,34],serializ:13,serializabl:13,serialized:13,serialized_dat:[11,12,13,15],serv:[9,29],servidor:[9,28,30],set:[20,26],set_connections:[11,12],settings:11,setup:[2,4],should:[11,13],shudtdown:[9,23,29],shutdown:[11,17],shutdown_os_signals:11,sid:[9,29],sigint:11,signal:[11,16],signalhandl:17,signals:[11,12,21],signif:[8,28],signific:24,sigterm:11,simpl:26,simplesmet:26,sinaliz:22,singleton:[],singletons:25,siz:11,sleep:[11,34],sobr:[9,23,26,29,30],something:11,sphinx:1,sse:[11,16,21,30,31],sse_conn:30,sse_rout:11,sseapplication:[],sseconnection:[11,12,30],sseconsum:18,ssemessag:18,sserout:11,stabl:26,stag:[11,13],start:[11,18],started:[11,13],starts:[11,13],startup:[9,11,17,23,29],stat:18,status:26,status_update_event:30,stop:11,stop_consum:13,stopping:13,str:[11,12,13,18,24],stre:[],strings:[],subclass:[11,12],submodul:21,subpackag:21,substitu:8,sucess:[26,28],suficient:26,suport:27,tag:[1,2,3,4,5,13],tak:16,tamanh:28,task:[11,30],task_runners:21,taskid:30,taskstatus:30,teh:28,temp:[8,9,27,28,29,32,34],tentant:30,ter:[7,8,28,34],test:[2,6,9],testcas:[],testing:21,text:[],tha:16,that:[11,12,13],the:[1,11,12,13,16],tick:11,tim:[13,21,34],timeit:[9,11,29,32],tip:[9,24,26,28,29],titlesonly:[],tiv:28,tod:[8,24,25,26,28],tom:28,top:26,torn:[25,31],total:34,traceback:34,track:[11,12],transactions:[11,34],transactions_key:11,trat:[8,28],tratament:28,triggered:[11,13],tru:[7,11,12,15,28,30],tud:9,type:[11,12,13,18,20,24,25,26,28,30,31,34],type_definition:20,typehints:26,types:26,types_registry:26,typesregistry:[20,26],typing:[11,12,13,28],unauthorized:26,uncaught:[11,13],undecodablemessageexception:13,union:[11,12,13,18],unparsed:11,url:[18,30],usa:28,usad:[24,28],usag:[11,12],usam:[8,22],usand:30,usar:[8,26],use:16,use_default_loop:7,used:[11,13],useful:13,user:[26,28,30,31],userdict:11,userlist:16,usernam:[11,13,18,28],using:16,uso:[9,22,31],utiliz:[22,25,34],utils:[21,34],vai:28,val:25,valid:[11,13],validate_method:11,validation:11,valu:[11,12],valueerror:[11,13,14],vari:25,vars:[],vej:26,vem:26,ver:[27,28],vez:[2,28,34],vhost:[11,12,28,30,31,34],via:8,vid:[8,22,25],virtual:[11,12,28],virtual_host:13,voc:[7,8,9,24,25,27,28,30],wait_closed:22,wait_for_dat:18,waiting:11,was:[11,13],web:[26,30],web_request:11,web_routedef:11,when:[11,13],which:16,wik:[],wikiped:[],will:[11,13],with_typ:[11,12],words_to_index:25,work:[8,9,29],workers:[8,9,22],world:30,wrap:20,wraps:26,xablau:[28,34],xen:28,xxxxxxxxxxxxx:11},titles:["Changelog","0.10.0","0.10.1","0.11.0","0.11.1","0.11.2","Guia de desenvolvimento","Escrevendo Testes Unit\u00e1rios","Incompatibilidades","Bem vindos \u00e0 documenta\u00e7\u00e3o oficial do projeto Asyncworker","Introdu\u00e7\u00e3o","asyncworker package","asyncworker.connections package","asyncworker.easyqueue package","asyncworker.exceptions package","asyncworker.rabbitmq package","asyncworker.signals package","asyncworker.signals.handlers package","asyncworker.sse package","asyncworker.testing package","asyncworker.types package","asyncworker","Hooks de startup e shudtdown","Asyncworker App","Sobre a classe principal App","Compartilhamento de dados e inicializa\u00e7\u00f5es ass\u00edncronas","HTTP","Tipos de Handlers","RabbitMQ","Guia de uso","In\u00edcio r\u00e1pido","Atualizando sua App Asyncworker","Utilit\u00e1rios","Rodando uma fun\u00e7\u00e3o em um intervalo fixo de tempo","Timeit"],titleterms:{"a\u00e7\u00e3":28,"ass\u00edncron":25,"atrav\u00e9s":30,"c\u00f3dig":28,"class":24,"fun\u00e7\u00e3":33,"in\u00edci":30,"m\u00faltipl":34,"prop\u00f3sit":[],"r\u00e1p":30,"requisi\u00e7\u00f5":30,"transa\u00e7\u00f5":34,"unit\u00e1ri":7,"utilit\u00e1ri":32,Uma:28,adicion:28,amqpconnection:28,and:9,apen:26,aplic:26,app:[11,22,23,24,25,31],armazen:25,asyncwork:[9,11,12,13,14,15,16,17,18,19,20,21,23,24,31],atualiz:31,backends:[],bas:[16,17],bem:9,bucket:11,bulk_siz:28,cad:28,camp:28,changelog:0,compartilh:25,complet:28,conf:11,connection:13,connections:[11,12],consum:[11,18,30],contents:[11,12,13,14,15,16,17,18,19,20],context:34,cri:24,customiz:26,dad:[25,28,30],decorator:[26,28,34],decorators:26,defin:24,desenvolv:6,document:9,easyqueu:13,endpoint:30,envs:26,escolh:[26,28],escrev:7,escut:26,estar:26,events:30,exceptions:[11,13,14],exempl:28,fil:30,fix:33,flush:28,gerenc:34,gui:[6,29],handl:26,handlers:[17,24,26,27],hooks:22,http:[17,26,30],incompatibil:8,indic:9,individual:28,inicializ:25,interval:33,introdu:10,lend:30,mensg:28,messag:[13,15,18],modul:[11,12,13,14,15,16,17,18,19,20],not:28,nov:24,oficial:9,onde:26,options:[11,28],packag:[11,12,13,14,15,16,17,18,19,20],par:[26,28],parametr:28,parametriz:26,port:26,prefetch:28,principal:24,projet:9,queu:13,rabbitmq:[15,17,28,30],receb:[26,28,30],registry:20,request:26,resolv:20,rod:[30,33],rout:[11,26,28],run_on_shutdown:22,run_on_startup:22,ser:28,serv:[26,30],shudtdown:22,sid:30,signals:[16,17],sobr:[24,28],sse:[17,18],startup:22,submodul:[11,13,15,16,17,18,20],subpackag:[11,16],tabl:9,task_runners:11,temp:33,test:7,testing:[11,19],tim:11,timeit:34,timeout:28,tip:27,types:20,uso:29,utils:11,valor:28,vind:9,work:30}})