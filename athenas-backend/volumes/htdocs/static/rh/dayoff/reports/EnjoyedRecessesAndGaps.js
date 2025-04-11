Ext._define('rh.reports.EnjoyedRecessesAndGaps', {
    extend: 'toolkit.widget.TabPanel',


    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelWidth: 100,
                autoHeight: true,
                items: [
                    this.getEmployeeField()
                ]
            });

        return this._formPanel;
    },

    getEmployeeField: function () {
        if (!this._employeefield)
            this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'servidor',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 350
            });

        return this._employeefield;
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
                                title: 'Recessos e Folgas - Usufruídos',
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

        engine.mq.Report.request({
            report: '/to/mpe/rh/dayoff/usufruidos',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'recessos_folgas_usufruidos',
                    report_name: 'Recessos e Folgas - Usufruídos',
                    employee_id: this.getEmployeeField().getValue()
                }
            ),
        });
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
                title: 'Recessos e Folgas - Usufruídos',
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

        rh.reports.EnjoyedRecessesAndGaps.superclass.constructor.call(this, cfg);
	}
});