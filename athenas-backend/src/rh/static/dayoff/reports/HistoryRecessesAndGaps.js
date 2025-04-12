Ext._define('rh.reports.HistoryRecessesAndGaps', {
    extend: 'toolkit.widget.TabPanel',


    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelWidth: 100,
                autoHeight: true,
                items: [
                    this.getEmployeeField(),
                    this.getPeriodField(),
                    this.getEmployeeType()
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

    getPeriodField: function () {
        if (!this._period)
            this._period = Ext._create('core.fields.AutocompleteField', {
                name: 'groupperiod',
                rest: 'rh.dayoff.groupperiod.Restful',
                fieldLabel: 'Período',
                width: 350
            });

        return this._period;
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
                                title: 'Histórico de Usufruto e Folgas',
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

    getEmployeeType: function(){
        if(!this._employeetype){
            this._employeetype = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Tipo do Servidor',
                hiddenName: 'tipo',
                ativo: 'tipo',
                width: 350,
                triggerAction: 'all',
                store: [
                    ['S', 'SERVIDOR'],
                    ['M', 'MEMBRO DO MINISTÉRIO PÚBLICO']
                ],
            });
        }

        return this._employeetype;
    },

    getMonthField: function () {
        if (!this._monthField) {
            this._monthField = new Ext.form.ComboBox({
                fieldLabel: 'Mês',
                hiddenName: 'mes',
                width: 350,
                store: [
                    ['01', 'JANEIRO'],
                    ['02', 'FEVEREIRO'],
                    ['03', 'MARÇO'],
                    ['04', 'ABRIL'],
                    ['05', 'MAIO'],
                    ['06', 'JUNHO'],
                    ['07', 'JULHO'],
                    ['08', 'AGOSTO'],
                    ['09', 'SETEMBRO'],
                    ['10', 'OUTUBRO'],
                    ['11', 'NOVEMBRO'],
                    ['12', 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._monthField;
    },

    getYearField: function(){
        if(!this._yearField)
            this._yearField = Ext._create('Ext.form.TextField', {
                name: 'year',
                fieldLabel: 'Ano',
                width: 350
            });

        return this._yearField;
    },

    generate: function () {

        engine.mq.Report.request({
            report: '/to/mpe/rh/dayoff/historico',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'recessos_folgas_historico',
                    report_name: 'Histórico de Usufruto e Folgas',
                    employee_id: this.getEmployeeField().getValue(),
                    period_id: this.getPeriodField().getValue(),
                    tipo: this.getEmployeeType().getValue(),
                }
            ),
        });
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
                title: 'Histórico de Usufruto e Folgas',
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

        rh.reports.HistoryRecessesAndGaps.superclass.constructor.call(this, cfg);
	}
});