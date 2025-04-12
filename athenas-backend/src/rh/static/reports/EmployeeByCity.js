Ext._define('rh.reports.EmployeeByCityReport', {
    extend: 'toolkit.widget.TabPanel',


    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                autoHeight: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Cidade',
                        name: 'municipio',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.localidade.Restful',
                        width: 260,
                        preFilter: [
                            {
                                'property': 'estado__sigla',
                                'value': 'MT',
                                'stage': 9999
                            }
                        ],
                        gridConfig: {
                            allowCreate: false,
                            allowRemove: false,
                            allowUpdate: false,
                            columnAction: false,
                            configOrderToolBar: ['search'],
                            hideColumns: ['valor_vale_transporte', 'ibge', 'distancia_capital', 'nome', 'microregiao_unicode', 'sede_termo', 'siafi', 'comarca_unicode', 'cep', 'estado_unicode', 'indicador_municipio', 'descricao', 'sigla']
                        },
                    },
                ]
            });

        return this._formPanel;
    },

    getMain: function () {
        if (!this._panel)
            this._panel = Ext._create('Ext.Panel', {
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: { tag: 'center' },
                items: [
                    {
                        region: 'center',
                        border: false,
                        items:[
                            {
                                xtype: 'fieldset',
                                title: 'Quantidade de Membros/Servidores por Município',
                                width: "33%",
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
                                    this.getFormPanel(),
                                    {
                                        xtype: 'button',
                                        iconCls: 'icon-siatu icon-siatu-move-down',
                                        style: 'margin-top: 10px',
                                        text: 'Gerar Relatório',
                                        width: 100,
                                        height: 25,
                                        scope: this,
                                        handler: this.generate,
                                    }
                                ]
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function () {

        var values = this.getFormPanel().getForm().getValues();
        if ((values.municipio === 'undefined') || (values.municipio === "")) {
            values.municipio = 'm';
        }

        engine.mq.Report.request({
            report: '/mt/mpe/rh/servidor/quantidade_por_municipio',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                values,
                {
                    outfile: 'quantidade_por_municipio_' + new Date().format("d/m/Y"),
                    report_name: 'Relatório - Quantidade de Membros/Servidores por Município',
                }
            ),
        });
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
                title: 'Relatório -> Quantidade de Membros/Servidores por Município',
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
                    this.getMain(),
                ],
			}
		);

        rh.reports.EmployeeByCityReport.superclass.constructor.call(this, cfg);
	}
});