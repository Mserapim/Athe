Ext._define('rh.gestorbatida.gestor_batidas.PeriodoWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gestorbatida.gestor_batidas.Restful',

    width: 600,

    servidorRecord: null,

    getFormPanel: function() {
        if(!this._formPanel){
            var servidorRecord = this.servidorRecord || {};

            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Nome',
                        name: 'employee_name',
                        value: servidorRecord.employee_nome || ''
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Matrícula',
                        name: 'employee_matricula',
                        value: servidorRecord.employee_matricula || ''
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Tipo',
                        name: 'employee_tipo',
                        value: servidorRecord.employee_tipo || ''
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Cargo',
                        name: 'employee_cargo',
                        value: servidorRecord.employee_cargo || ''
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Lotação',
                        name: 'employee_lotacao',
                        value: servidorRecord.employee_lotacao || ''
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Jornada de Trabalho',
                        name: 'jornada_trabalho',
                        value: servidorRecord.jornada_trabalho || ''
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Carga Horária Semanal',
                        name: 'duracao',
                        value: servidorRecord.duracao || ''
                    },
                    {
                        xtype: 'datefield',
                        fieldLabel: 'Data Início',
                        name: 'data_inicio',
                        format: 'd/m/Y',
                        allowBlank: false
                    },
                    {
                        xtype: 'datefield',
                        fieldLabel: 'Data Fim',
                        name: 'data_fim',
                        format: 'd/m/Y',
                        allowBlank: false
                    },
                    this.getTipoField(servidorRecord),
                    {
                        xtype: 'textarea',
                        fieldLabel: 'Observação',
                        name: 'justificativa',
                        anchor: '100%'
                    },
                ],
            });
        }
            
        return this._formPanel;
    },

    getPk: function (cfg) {
        if (this._pk) {
            return this._pk;
        }

        this._pk = Ext._create('Ext.form.Hidden', {
            name: 'pk',
        });

        return this._pk;
    },

    getTipoField: function (servidorRecord) {
        if (this._tipoField) {
            return this._tipoField;
        }

        this._tipoField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Tipo de justificativa',
            hiddenName: 'type',
            displayField: 'description',
            valueField: 'pk',
            triggerAction: 'all',
            editable: false,
            allowBlank: false,
            anchor: '99%',
            store: Ext._create('Ext.data.Store', {
                proxy: Ext._create('Ext.data.HttpProxy', {
                    method: 'GET',
                    disableCaching: false,
                    url: core.callAction(
                        'RHGestorBatidas',
                        'get_tipo_justificativa',
                        [servidorRecord.employee_matricula]
                    )
                }),
                reader: Ext._create('Ext.data.JsonReader', {
                    idProperty: 'pk',
                    fields: [
                        'pk',
                        'description',
                    ],
                    root: 'collection',
                    totalProperty: 'count',
                }),
                autoLoad: true,
            }),
        });

        return this._tipoField;
    },

    getJustificativaField: function (cfg) {
        if (this._contentField) {
            return this._contentField;
        }

        this._contentField = Ext._create('toolkit.fields.CKEditor', {
            name: 'content',
            fieldLabel: 'Texto da justificativa',
            height: 300,
            allowBlank: false,
        });

        return this._contentField;
    },

    _getValues: function () {
        var display = this.getTipoField().getRawValue();
        var attachments = [];
    
        if (typeof this.getAttachmentGrid === 'function') {
            attachments = this.getAttachmentGrid().getStore().getRange().map(function(record) {
                return JSON.parse(JSON.stringify(record.data));
            });
        }
    
        return {
            pk: this.getPk().getValue() || null,
            type: {
                value: this.getTipoField().getValue(),
                display: display ? `JUSTIFICATIVA ${display}` : '',
            },
            content: this.getJustificativaField().getValue(),
            attachments: attachments,
        };
    },

    save: function() {
        var form = this.getFormPanel().getForm();
        if (form.isValid()) {
            var values = form.getValues();

            var dataInicio = values.data_inicio.split('/');
            if (dataInicio.length === 3) {
                var dataInicioFormatada = dataInicio[2] + '-' + dataInicio[1] + '-' + dataInicio[0];
                values.data_inicio = dataInicioFormatada;
            }
    
            if (values.data_fim) {
                var dataFim = values.data_fim.split('/');
                if (dataFim.length === 3) {
                    var dataFimFormatada = dataFim[2] + '-' + dataFim[1] + '-' + dataFim[0];
                    values.data_fim = dataFimFormatada; 
                }
            }

            Ext.Ajax.request({
                url: core.callAction('RHGestorBatidas', 'salvarbatida'),
                method: 'POST',
                params: {
                    employee: this.servidorRecord.employee_id,
                    tipo_justificativa: values.type,
                    justificativa: values.justificativa,
                    data_inicio: values.data_inicio,
                    data_fim: values.data_fim,
            },
            scope: this,
            success: function(response) {
                var resp = Ext.decode(response.responseText);
                if (resp.success) {
                    this.close();
                } else {
                    Ext.Msg.alert('Erro', resp.message);
                }
            },
            failure: function(response) {
                Ext.Msg.alert('Erro', 'Erro ao enviar solicitação ao servidor');
            },
        });
    }
},

    constructor: function(cfg) {
        this.servidorRecord = cfg.servidorRecord || {};

        Ext.applyIf(cfg, {
            title: 'Justificativa por Período',
            items: this.getFormPanel()
        });

        rh.gestorbatida.gestor_batidas.Window.superclass.constructor.call(this, cfg);
    },

});