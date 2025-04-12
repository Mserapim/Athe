
 Ext._define('rh.queryregistration.TagsWindow', {
    extend: 'rh.queryregistration.ConsultationWindow',

    rest: 'rh.queryregistration.ConsultationRestful',
    width:700,


    getArrayIds: function(list_ids){
        var result = new Array()
        var array = list_ids.slice(1, -1).split(',');

        array.forEach(item=>{
            item = item.split(" ").join("")
            result.push(Number(item.slice(1,-1)));

        })
        return result

    },
    
    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: this.getTabPanel(cfg)
            });

            

        return this._formPanel;
    },

    getTabPanel: function (cfg) {
        var fields = this.createForm(cfg)
        var keys = Object.keys(fields)
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                border: false,
                height: 480,
                activeTab: 0,
                deferredRender:false,
                items: this.creteFormPanel(keys,fields)
            });

        return this._tabPanel;
    },


    creteFormPanel:function(keys,fields){
        panels =  []
        keys.forEach(element => {
            panels.push(
                Ext._create('Ext.Panel', {
                    layout:"form",
                    frame: true,
                    border: false,
                    title: element,
                    items:[
                        fields[element],
                    ]
                })
            )
           
        }) 
        return panels
    },


    createForm:function(cfg){
       fields = {"Principal":[]}
       cfg.data.forEach(element => {
           if (element['type'] == 'multiselectfield'){
                if (fields[element['name']] == undefined)
                    fields[element['name']] = []
                fields[element['name']].push(
                    {
                        xtype:'fieldset',
                        title: element['label'],
                        items:[
                            this._mult = Ext._create('toolkit.plugins.MultiSelectField', {
                                fieldLabel: element['label'],
                                name: element['tag'],
                                hideLabel:true,
                                hiddenName: element['tag'],
                                controller: element['controller'],
                                anchor: '99%',
                                conf: {
                                    canAdd: false,
                                    canEdit: false
                                },
                                displayField: 'unicode',
                                valueField: element['valuefield'],
                            })
                        ]
                    },        
                
                );

           }else if (element['type'] == 'checkboxchoicefield'){
                if (fields[element['name']] == undefined)
                    fields[element['name']] = []
                fields[element['name']].push(
                    {
                        xtype:'fieldset',
                        title: element['label'],
                        items:[
                            {
                                xtype: element['type'],
                                singleSelection: false,
                                checkconfig: {
                                    name: element['tag'],
                                    hideLabel: true,
                                    choiceId: element['choice'],
                                    valueField:element['valuefield'],
                                    columns: element['colums'],
                                    items_db: element['tag_value'],
                                    // preFilter: [
                                    //     {property: 'value__in', value: [1, 20, 21], stage: 100},
                                    // ],

                                },
                            }
                        ]
                    }
                );
           }else{
                fields['Principal'].push(
                    {
                        name: element['tag'],
                        fieldLabel: element['label'],
                        xtype: element['type'],
                        allowBlank: true,
                        maxLength: element['length'],
                        rest: element['rest'],
                        anchor: '99%',
                        value: element['tag_value'],
                        hiddenName:element['tag'],
                        choiceId:element['choice'],
                        valueField:element['valuefield'],
                        format:element['format'],
                        withNone:true,
                        withNoneLabel:"TODOS",
                        defaultValue:9999,
                    }
                )
            }    
        });

        fields['Principal'].push(
            {
                hiddenName:'orientation',
                fieldLabel:"Modo",
                xtype:'choicefield',
                choiceId:'queryregistration.PAGE_ORIENTATION',
                anchor: '99%',
                allowBlank: true,
                value:2
            },

        )


        return fields

    },


    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Relatório',
                    width: 100,
                    height: 25,
                    scope: this,
                    menu:{
                        scope: this,
                        items: [
                            {
                                text: 'Arquivo PDF ',
                                type: 'PDF',
                                iconCls: 'icon-ged icon-ged-application-pdf',
                                scope: this,
                                handler: function () {
                                    this.getReport(cfg,'create_pdf')
                                    this.destroy()
                                }
                            },
                            // {
                            //     text: 'Arquivo ODT',
                            //     type: 'ODT',
                            //     iconCls: 'icon-ged icon-ged-application-msword',
                            //     scope: this,
                            //     handler: function (item) {
                            //         this.build(item.type);
                            //     }
                            // },
                            {
                                text: 'Arquivo XLS',
                                type: 'XLS',
                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                scope: this,
                                handler: function (item) {
                                    this.getReport(cfg,"create_xls")
                                    this.destroy()
                                }
                            },
                        ]
                    }
                },            
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

        return this._buttons;
    },

    setMultiChoiceValue:function(cfg,params){
        cfg.multichoices.forEach(element =>{
            for (var data in params) {
                aux = data
                if (data.slice(0, data.search(/\d/)) == element){
                    if (params[element])
                        params[element].push(params[aux])
                    else
                        params[element] = [params[aux]]   
                    delete params[aux]
                }
                   
            }
        
        })
      
    },

    makeid: function (length) {
        var result           = '';
        var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var charactersLength = characters.length;
        for ( var i = 0; i < length; i++ ) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    },

    getReport: function(cfg,method){       
        var params = this.getFormPanel().getForm().getValues(); 
        var name_observer = this.makeid(5);
        this.setMultiChoiceValue(cfg,params)
        if (params) {
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('QueryReport', method),
                params: {
                    tags:JSON.stringify(params),
                    pk:cfg.pk,
                    name_observer:name_observer,
                },
                success: function (request) {
                    var obj = Ext.decode(request.responseText);
                    if (obj.success){
                        Ext.Msg.show({
                            title: 'Solicitando Relatório',
                            msg: obj.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                        this.scope.getStore().reload();
                        if (obj.download)
                            var RemoteObserver = core.RemoteObserver;
                            var cb = RemoteObserver.on(name_observer, {
                                scope: this,
                                fn: function (data) {
                                    setTimeout(
                                        function() {
                                            if (data.status == 'failed') {
                                                RemoteObserver.un(name_observer, {scope: this})
                                            } else {
                                                toolkit.util.downloadFile({
                                                    url: data.path,
                                                    filename: data.filename,
                                                    approach: 'download',
                                                });;
                                                RemoteObserver.un(name_observer, {scope: this})
                                            }
                                        
                                        },
                                        1000
                                    );
                                
                                }
                            });
                        
                    }else{
                        Ext.Msg.show({
                            title: 'Error',
                            msg: obj.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }     
                },
                failure: function (request) {
                    Ext.Msg.show({
                        msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },
                scope: this
            });
        }
        else
            Ext.Msg.show({
                msg: 'Primeiro selecione os parâmetros',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            })
	
    },

    
    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            title: 'Parâmetros',
            items: this.getFormPanel(cfg)
        });

        Ext.apply(cfg, {
          
        });

        rh.queryregistration.TagsWindow.superclass.constructor.call(this, cfg);
    }


});