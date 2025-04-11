
Ext._define('judicial.reports.ExecutionOrgansReport', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(params)
    {
        params = params || {};

        var cfg = Object.assign({
            title: 'Relatório de Cargos em Execução',
            padding: 5,
            items: [this.getFormPanel()]
        }, params);

        judicial.reports.ExecutionOrgansReport.superclass.constructor.call(this, cfg);
    },

    getComboField: function()
    {
        if(!this._combo)
            this._combo = Ext._create('Ext.form.ComboBox', {
                xtype: 'combo',
                triggerAction: 'all',
                mode: 'local',
                name: 'execution_organ',
                store: Ext._create('Ext.data.ArrayStore', {
                    fields: ['value', 'displayText'],
                    data: [
                        [1, 'Todos'],
                        [2, '1ª Entrância'],
                        [3, '2ª Entrância'],
                        [4, '3ª Entrância'],
                        [5, 'Procuradorias']
                    ]
                }),
                valueField: 'value',
                displayField: 'displayText',
                value: 1,
                width: 150,
            });
        return this._combo;
    },

    generate: function (type) {

        var combo = this.getComboField(),
            store = combo.getStore(),
            value = combo.getValue(),
            index = store.find('value', value),
            record = store.getAt(index),
            text = record.get('displayText');

        engine.mq.Report.request({
            report: '/to/mpe/judicial/execution_organ',
            waitMessage: 'Gerando relatório...',
            params: {
                report_name: 'Cargos em Execução - '  + text,
                outfile: 'cargos-em-execucao-' + toolkit.util.slugify(text),
                execution_organ: value
            }
        }, type);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                padding:'5px 10px',
                autoHeight: true,
                items: [
                    {
                        xtype: 'compositefield',
                        fieldLabel: 'Entrância',
                        scope: this,
                        items: [
                            this.getComboField(),
                            {
                                xtype: 'button',
                                scope: this,
                                tooltip: 'Gerar relatório de cargos em execução',
                                text: 'Gerar relatório',
                                padding: '2px 5px',
                                menu: {
                                scope: this,
                                items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo ODT',
                                    type: 'ODT',
                                    iconCls: 'icon-ged icon-ged-application-msword',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo XLS',
                                    type: 'XLS',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(item.type);
                                    }
                                },
                                ]
                                },
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },
});
