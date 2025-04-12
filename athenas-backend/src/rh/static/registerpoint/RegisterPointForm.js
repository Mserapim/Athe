/*****************************************************************************
*                                                                            *
*                     REGISTRAR PONTO                   *
*                                                                            *
*****************************************************************************/
Ext._define('rh.registerpoint.RegisterPointForm', {
    extend: 'Ext.FormPanel',

	_register: function(){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'RHRegisterPoint',
                    'register_point'
                ),
                params: {
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if (obj.mark)
                        console.info(obj.mark)
                        if (obj.mark == 1){
                            this.getStartButton().disable()
                            this.getEndButton().enable()
                        }else{
                            this.getStartButton().enable()
                            this.getEndButton().disable()
                        }
                        
                    if(obj.success){
                        Ext.Msg.show({
                            title: 'Registro de Ponto',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });

                    }
                    else
                        Ext.Msg.show({
                            title: 'Registro de Ponto',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                                
                    },

                failure: function() {
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                    });
                },
                scope: this
            });
    },

    _getMark: function(cfg){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'RHRegisterPoint',
                'get_mark'
            ),
            params: {
            },
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                if(obj.success)
                    if (obj.mark == 1)
                        this.getStartButton().disable()
                    else
                        this.getEndButton().disable()

                        
            },
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
    },

    getStartButton: function(cfg) {
        if (this._startButton) {
            return this._startButton;
        }

        this._startButton = Ext._create('Ext.Button', {
            text: 'Início',
            scope: this,
            //width:200,
            iconCls: 'icon-judicial icon-ejud-outlawcortsuit-have-time',
            style:'margin-top:35px',
            handler: function () {
                this._register(cfg);
            },
        });

        return this._startButton;
    },

    getEndButton: function(cfg) {
        if (this._endButton) {
            return this._endButton;
        }

        this._endButton = Ext._create('Ext.Button', {
            text: 'Fim',
            scope: this,
            //width:200,
            style:'margin-top:35px',
            iconCls: 'icon-judicial icon-ejud-outlawcortsuit-have-time',
            handler: function () {
                this._register(cfg);
            },
        });

        return this._endButton;
    },

    constructor: function (cfg) {
        cfg = cfg || {};
        this._getMark(cfg)
        Ext.apply(cfg, {
            border: false,
            labelWidth: 80,
            region: 'center',
            //bodyStyle: "padding:1.0vw 0vw 0vw 6.0vw",
            bodyStyle: "padding:1.0vw 0vw 0vw 0vw",
            items: [
                {
                    region: 'center',
                    border: false,
                    items: [
                        {
                            xtype: 'displayfield',
                            name: 'hour',
                            style: 'font-size:2.2vw;',
                            id:'clock',
                        }
                    ],
                }
            ],
            buttonAlign: 'center',
            buttons: [ 
                this.getStartButton(cfg),
                this.getEndButton(cfg) 
            ],
        });

        var task = {
            run: function(){
                Ext.getCmp('clock').setValue(new Date().toLocaleTimeString('pt-BR',{timeZone:'America/Cuiaba'}));
            },
            interval: 100 //
        }
        Ext.TaskMgr.start(task);
        rh.registerpoint.RegisterPointForm.superclass.constructor.call(this, cfg);
    },
});
