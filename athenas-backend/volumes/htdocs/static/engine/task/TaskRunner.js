/**
 *
 **/
Ext._define('engine.TaskRunner', {
    extend: 'Ext.ToolTip',    

    tplToolTip: function(){
        if(!this._tplToolTip){
            this._tplToolTip = new Ext.XTemplate(
                '<tpl>',
                    '<div style="width:438px; max-height:200px; display:block; overflow:auto;">',
                        '&nbsp>>&nbsp{msg}',  // use current array index to autonumber
                    '</div>',
                '</tpl>',
                {
                    // XTemplate configuration:
                    compiled: true,
                    disableFormats: true,
                }
            );
        }
        return this._tplToolTip;
    },

    getButtonStatus: function(){
        if(!this._buttonStatus){
            this._buttonStatus = new Ext.Button({
                iconCls: 'icon-core icon-core-blank',
                width: 20
            });
        }
        return this._buttonStatus;
    },

    getInfoBottomBar: function(){
        if(!this._infoBottomBar){
            this._infoBottomBar = new Ext.Toolbar.TextItem({
                text: 'Carregando informações da tarefa'
            });
        }
        return this._infoBottomBar;
    },

    updateTopToolBar: function(){
        if(!this.hidden){
            // if(this.task.finished_task)
            //     this.getTool('close').show();
            // else
            //     this.getTool('close').hide();

            if(this.task.has_messages)
                this.getTool('search').show();
            else
                this.getTool('search').hide();
            
            if(this.task.has_files)
                this.getTool('down').show();
            else
                this.getTool('down').hide();
        }
    },

    updateBottomBar: function(htmlOrData){
        var cmp_info = this.getInfoBottomBar();
        var cmp_status = this.getButtonStatus();
        if(this.task && this.task.finished_task){
            cmp_info.update(this.task.status_display);
            if(this.task.status == 'ERROR')
                cmp_status.setIconClass('icon-core icon-core-run-with-error');
            else
                cmp_status.setIconClass('icon-core icon-core-run-ok');
        }else{
            if(this.task.pct && this.task.total)
                cmp_info.update('Processando '+this.task.pct+ ' de '+this.task.total);
            else if(this.task.pctText)
                cmp_info.update(this.task.pctText);
            else
                cmp_info.update(this.task.status_display);

            cmp_status.setIconClass('icon-core icon-core-waiting');
        }
    },

    getBottomBar: function(cfg){
        if(!this._bottomBar){
            this._bottomBar = new Ext.Toolbar({
                id: 'bbar'+cfg.task.sid,
                items:[
                    this.getButtonStatus(),
                    this.getInfoBottomBar()
                ]
            })
        }
        return this._bottomBar;
    },

    updateTaskToolTip: function(cfg){
        cfg = cfg || {};
        Ext.apply(this.task, cfg);
        this.updateTopToolBar();
        if(this.task.msg){
            this.update({msg:this.task.msg});
        }
        if(this.task.description){
            this.setTitle(this.task.description);
        }
        if(this.task.finished_task){
            console.debug('TASK '+this.task.sid+ ' is done!');
            if(this._taskMgr)
                Ext.TaskMgr.stop(this._taskMgr);
        }
        this.updateBottomBar();
    },

    getTaskInformation: function(){
        var rest = new engine.TaskRunnerRestful();
        var cfg = {
            params: {
                sid: this.task.sid,
            },
            success: function(request) {
                var result = Ext.decode(request.responseText);
                if(result.success)
                    this.updateTaskToolTip(result.instance);
                else{
                    Ext.TaskMgr.stop(this._taskMgr);
                }
            },
            failure: function() {
                console.debug("Erro ao carregar notificações...");
            },
            scope: this
        };

        Ext.apply(cfg, rest.getRoute('read', this.task.pk));

        Ext.Ajax.request(cfg);
    },

    startTaskToolTip: function(){
        var scope = this;
        if(!this._taskMgr){
            cfg = {   
                run: function(){
                    scope.getTaskInformation(scope.task.sid)
                },
                //TODO Refactoring to config option in an file config or system config
                interval: 5 * 1000 //5 seconds
            }            
            this._taskMgr = Ext.TaskMgr.start(cfg);
        }else
            Ext.TaskMgr.start(this._taskMgr);

    },

    stopTaskToolTip: function(){
        var scope = this;
        if(this._taskMgr)
            Ext.TaskMgr.stop(this._taskMgr);
        else
            console.debug('Não existe task!');
    },

    actionClose: function(event, toolEl, panel, tc){
        console.debug('CLOSE TOOLTIP WITH SID '+ this.task.sid);
        toolkit.util.Tasks.closeTaskToolTip(this);
    },

    actionDetail: function(event, toolEl, panel, tc){
        new engine.TaskSessionWindow({
            oId:this.task.pk,
            title: this.title,
            values: 'remote',
            disableSave: true,
            activeTab: 1,
            modal: false,
        }).show();
    },

    actionStop: function(event, toolEl, panel, tc){
    },

    actionDownloads: function(event, toolEl, panel, tc){
    },

    setVisualized: function(callback){
        var rest = new engine.TaskRunnerRestful();
        var cfg = {
            params: {
                visualized: true,
            },
            success: function(request) {
                var result = Ext.decode(request.responseText);
                console.debug('TaskToolTip '+ this.task.sid+ ' visualized!');
                if(callback){
                    callback();
                }

            },
            failure: function() {
                console.debug("Erro ao atualizar task para visualizada!");
            },
            scope: this
        };

        Ext.apply(cfg, rest.getRoute('update', this.task.pk));

        Ext.Ajax.request(cfg);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg.task, {
            total:100
        });

        Ext.apply(
            cfg,
            {
                title: '<b>'+(cfg.task.description? cfg.task.description: 'Tarefa em execução')+'</b>',
                id: 'task'+cfg.task.sid,
                progress: (cfg.task.progress && true) || false,
                layout:'fit',
                floating: true,
                width: 450,
                shadow: false,
                data: {msg:'Teste de tarefa....'},
                tpl: this.tplToolTip(),
                autoHide: false,
                hidden: true,
                closable: true,
                bbar: this.getBottomBar(cfg),
                tools:[{
                    id:'down',//gear
                    qtip: 'Downloads',
                    hidden: true,
                    handler: this.actionDownloads,
                    scope: this
                },{
                    id:'search',//gear
                    qtip: 'Detalhes',
                    handler: this.actionDetail,
                    hidden: true,
                    scope: this
                },{
                    id:'close',//gear
                    qtip: 'Fechar',
                    handler: this.actionClose,
                    // hidden: true,
                    scope: this
                }],
                listeners: {
                    show: function(p){
                        // console.debug('BEFORERENDER '+p.id);
                        this.startTaskToolTip();
                        this.updateTaskToolTip();
                    },
                    hide: function(p){
                        // console.debug('RENDER '+p.id);
                        this.stopTaskToolTip();
                    },
                    destroy: function(p){
                    },
                    scope: this
                }                
            }
        );
        // console.debug(cfg);

        // this.callParent([cfg]);
        engine.TaskRunner.superclass.constructor.call(this, cfg);
        // this.startTaskToolTip();     
    }
});

Ext._define('engine.TaskRunnerRestful',{
    extend: 'core.Restful',
    resource: 'CommandControllerTaskViewer',

    getFields: function() {
        if(!this._fields)
            this._fields = engine.TaskRunnerRestful.superclass.getFields.call(this).concat([        
                {name: 'started_task', type: 'date'},
                {name: 'finished_task', type: 'date'},
                {name: 'user', type: 'int'},
                {name: 'user_unicode', type: 'string'},
                {name: 'sid', type: 'string'},
                {name: 'params_cache', type: 'string'},
            ]);
        return this._fields;
    },    
});

