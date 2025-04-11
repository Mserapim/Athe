/**
 *
 **/

Ext._define('rh.gfp.reports.PayCheckManage', {
	extend: 'toolkit.widget.TabPanel',

	_generatePaycheck: function(){
        if(this.getEmployeeField().getValue() && this.getStartField().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'RelatorioContracheque',
                    'generate_report'
                ),
                params: {
                    employee: this.getEmployeeField().getValue(),
                    type: this.getPayrollTypeField().getValue(),
                    start: this.getStartField().getValue(),
                    end: this.getEndField().getValue()
                },
                success: function(request) {
					var obj = Ext.decode(request.responseText);
					Ext.Msg.show({
                        title: 'Solicitando Relatório',
                        msg: obj.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    //var result = Ext.decode(request.responseText);
                    //this._buildPaycheck(result.list_paycheck);
                },
                failure: function() {
                    alert('Ocorreu um erro tentando excluir os subitems selecionados.');
                },
                scope: this
            });
        }else Ext.Msg.show({
            msg: 'Selecione Tipo folha e Periodo',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

	// _buildPaycheck: function(paycheck){

    //     var employee = this.getEmployeeField().getComboField().lastSelectionText;
	// 	var type = this.getPayrollTypeField().getComboField().lastSelectionText;
    //     var start = this.getStartField().getValue();
    //     var end = this.getEndField().getValue();

    //     engine.mq.Report.request({
    //         report: '/to/mpe/gfp/paycheck_by_id',
    //         waitMessage: 'Gerando relatório...',
    //         params: {

    //             outfile: 'contracheque' + employee + '-' + type + '-' + start + '-' + end,
    //             report_name: 'Contra-cheque'  + ' - ' + employee + ' - ' + type + ' - ' + start + ' - ' + end,
    //             contracheque: paycheck,
    //             admin: 1
    //         }

    //     });
    // },

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 400
			});

		return this._employeefield;
	},

	getPayrollTypeField: function(){
		if(!this._typefield)
			this._typefield = Ext._create('core.fields.AutocompleteField', {
                name: 'type',
                rest: 'rh.gfp.payroll.PayrollTypeRestful',
                fieldLabel: 'Tipo folha',
                width: 400
			});

		return this._typefield;
	},

	getStartField: function(){
		if(!this._startfield)
			this._startfield = Ext._create('Ext.form.TextField', {
                name: 'start',
                fieldLabel: 'Inicio (mm/aaaa)',
				//emptyText:"Referência início -> Ex: 01/1900",
                width: 400
			});

		return this._startfield;
	},

	getEndField: function(){
		if(!this._endfield)
			this._endfield = Ext._create('Ext.form.TextField', {
                name: 'end',
                fieldLabel: 'Fim (mm/aaaa)',
				//emptyText:"Referência fim -> Ex: 01/1900",
                width: 400
			});

		return this._endfield;
	},

	getMain: function(){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 650,
		    split: true,
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	// title: 'Informações do Contra-Cheque',
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Impressão do Contra-Cheque',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getEmployeeField(),
	        			this.getPayrollTypeField(),
	        			this.getStartField(),
	        			this.getEndField(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Contra-cheque',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._generatePaycheck,
                    }
	        		]
	        	},
        		]
        	}
    		]
	    });

		return this._panel;
	},




	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Relatório -> Contra-cheque'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(),
				]
			}
		);

		// this.getCurrentPayroll();

		rh.gfp.reports.PayCheckManage.superclass.constructor.call(this, cfg);
	}
});