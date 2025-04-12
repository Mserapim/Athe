/*****************************************************************************
*                                                                            *
                        Informe de Rendimentos
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.CedulaCReport', {
    extend: 'Ext.FormPanel',

    /**
    * Metodo que retrona um Array contendo anos, partindo-se de uma data default (2023)
    * até o ano atual
    * @param initialYear: Integer opcional para subsbtituir a data inicial default
    */
    getYearStore: function(cfg, initialYear) {
        initialYear = initialYear || 2023;
        var currentYear = (new Date()).getFullYear();
        var store = [];
        for (var year = currentYear; year >= initialYear; year--)
            store.push([year, year.toString()]);
        return store;
    },

    getYearField: function(cfg) {
        if (!this._yearField)
            this._yearField = Ext._create('Ext.form.ComboBox', {
                name: 'year',
                fieldLabel: 'Ano',
                triggerAction: 'all',
                editable: false,
                store: this.getYearStore(),
                allowBlank: false,
                anchor: '97%'
            });
        return this._yearField;
    },

    getTypeField: function(cfg) {
        if (!this._typeField)
            this._typeField = Ext._create('Ext.form.ComboBox', {
                name: 'type',
                fieldLabel: 'Órgão Emissor',
                triggerAction: 'all',
                editable: false,
                store: [
                    ['MPMT', 'MPMT'],
                    ['TRE', 'TRE']
                ],
                anchor: '97%',
                allowBlank: true
            });
        return this._typeField;
    },
    
    /**
    * Metodo que faz chamada Ajax para Download de Cédula-C
    */
	generateCedulaCReport: function(){
        if(this.getYearField().getValue() &&
            this.getTypeField().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'CedulaCIRPF',
                    'create_pdf_cedula_c'
                ),
                params: {
                    year: this.getYearField().getValue(),
                    type: this.getTypeField().getValue(),
                    download: true
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.success){
                       this.sendEmiter(obj)

                       setTimeout( 
                            function() {
                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'CedulaCIRPF',
                                        'marker'
                                    ),
                                    params: {
                                        uuid: obj.uuid
                                    },
                                    success: function() {},
                                    failure: function() {},
                                });
                                RemoteObserver.un('cedula-c', {scope: this,})
                            },
                        2500);
                    }else{
                        Ext.Msg.show({
                            title: 'Informe de Rendimentos',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                    }       
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
        }else Ext.Msg.show({
            msg: 'Selecione o Ano e ou o Órgão Emissor para impressão da cédula.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    /**
    * Metodo que cria um Observer, pelo qual fará fará o download automático do documento
    * @param: obj.message Texto contendo ou mensagem de sucesso ou falha da requisição
    */
    sendEmiter: function(obj) {
        var RemoteObserver = core.RemoteObserver;
        tool = toolkit.util
        var cb = RemoteObserver.on('cedula-c', {
            scope: this,
            fn: function (data) {
                if(data){
                    setTimeout(
                        function() {
                            Ext.Msg.show({
                                title: 'Informe de Rendimentos',
                                buttons: Ext.Msg.OK,
                                msg: obj.message
                            });
                            
                            tool.downloadFile({
                                url: data.path,
                                filename: data.filename,
                                approach: 'download',
                            });
                        },
                        600
                    );

                    RemoteObserver.un('cedula-c', {scope: this,})
                }
            },
        });
    },

    getGenerateButton: function(cfg) {
        if (this._generateButton) {
            return this._generateButton;
        }

        this._generateButton = Ext._create('Ext.Button', {
            text: 'Gerar',
            scope: this,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: function () {
                this.generateCedulaCReport(cfg);
            },
        });

        return this._generateButton;
    },


    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 80,
            items: [
                this.getYearField(),
                this.getTypeField(),
            ],
            buttonAlign: 'left',
            buttons: [ this.getGenerateButton(cfg) ],
        });
        this.sendEmiter({message:"O Download do Informe de Rendimentos será iniciado em breve."})
        rh.gfp.reports.CedulaCReport.superclass.constructor.call(this, cfg);
    },
});

