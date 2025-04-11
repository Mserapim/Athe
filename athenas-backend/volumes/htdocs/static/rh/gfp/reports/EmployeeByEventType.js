/**
 *
 **/

Ext._define('rh.gfp.reports.EmployeeByEventType', {
	extend: 'toolkit.widget.TabPanel',

	_buildPaycheck: function (paycheck) {

		var payroll = this.getPayrollField().getComboField().lastSelectionText;
		var type = this.getEmployeeTypeField().getRawValue();
		console.log(this.getEmployeeTypeField().getRawValue());
		if(this.getPayrollField().getValue() == ''){
			Ext.Msg.show({
                title: 'Aviso',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'É necessário preencher a Folha'
            });
            return;
		}
		if(this.getEventField().getValue() == ''){
			Ext.Msg.show({
                title: 'Aviso',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'É necessário preencher o evento'
            });
            return;
		}

		engine.mq.Report.request({
			report: '/to/mpe/gfp/type_employee_by_event',
			waitMessage: 'Gerando relatório...',
			params: {

				outfile: 'Servidores da folha ' + payroll + ' - por tipo ' + type,
				report_name: 'Servidores da folha ' + payroll + ' - por tipo ' + type,
				folha: this.getPayrollField().getValue(),
				evento: this.getEventField().getValue(),
				tipo: this.getEmployeeTypeField().getValue(),
			}

		});
	},

	getPayrollField: function () {
		if (!this._payrollfield)
			this._payrollfield = Ext._create('core.fields.AutocompleteField', {
				name: 'payroll',
				rest: 'rh.gfp.payroll.PayrollRestful',
				fieldLabel: 'Folha',
				width: 400,
				allowBlank: false,
			});

		return this._payrollfield;
	},

	getEventField: function () {
		if (!this._eventField)
			this._eventField = Ext._create('core.fields.AutocompleteField', {
				name: 'event',
				rest: "rh.gfp.payroll.EventRestful",
				fieldLabel: 'Evento',
				width: 400,
				allowBlank: false,
			});

		return this._eventField;
	},

	getEmployeeTypeField: function () {
		if (!this._typefield)
			this._typefield = Ext._create('Ext.form.ComboBox', {
				hiddenName: 'employee_type',
				fieldLabel: 'Tipo',
				store: [
					['0', 'TODOS'],
					['M', 'MEMBRO'],
					['S', 'SERVIDOR']
				],
				triggerAction: 'all',
				value: '0',
			});

		return this._typefield;
	},

	getMain: function () {
		if (!this._panel)
			this._panel = new Ext.Panel({
				layout: 'border',
				region: 'center',
				height: 650,
				split: true,
				autoEl: { tag: 'center' },
				items: [
					{
						// title: 'Informações do Contra-Cheque',
						region: 'center',
						border: false,
						items: [
							{
								xtype: 'fieldset',
								title: 'Servidores por consignação e tipo',
								name: 'fieldServidor',
								width: "33%",
								style: 'margin: 5px',
								align: 'center',
								items: [
									this.getPayrollField(),
									this.getEventField(),
									this.getEmployeeTypeField(),
									{
										xtype: 'button',
										iconCls: 'icon-siatu icon-siatu-move-down',
										style: 'margin-top: 10px',
										text: 'Gerar',
										width: 100,
										height: 25,
										scope: this,
										handler: this._buildPaycheck,
									}
								]
							}
						]
					}
				]
			});

		return this._panel;
	},




	constructor: function (cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
				title: 'Servidores por consignação e tipo'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getMain(),
				]
			}
		);

		// this.getCurrentPayroll();

		rh.gfp.reports.EmployeeByEventType.superclass.constructor.call(this, cfg);
	}
});