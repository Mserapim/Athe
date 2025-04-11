Ext._define('rh.reports.PayCheckManage', {
	extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 200,
    CARD_WIDTH: 550,
    REGION: 'center',
    GAP: 50,
    LEFT_PADDING: 480,
    BOTTOM_PADDING: 100,

    _getDefaults: function () {
        return {
            flex: 1,
            height: this.CARD_HEIGHT,
            width: this.CARD_WIDTH,
            baseCls: 'x-river-panel',
            align: this.REGION,
        };
    },

	_generatePaycheck: function(){
        if(this.getEndCompetenceField().getValue() && this.getStartCompetenceField().getValue() && this.getEmployeeField().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'GPPayCheckReport',
                    'paycheck_list'
                ),
                params: {
                    end_competence: this.getEndCompetenceField().getValue(),
                    start_competence: this.getStartCompetenceField().getValue(),
                    employee: this.getEmployeeField().getValue()
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.success)
                        this._buildPaycheck(obj.list_paycheck);
                    else
                        Ext.Msg.show({
                            title: 'Holerite',
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
        }else Ext.Msg.show({
            msg: 'Selecione Tipo folha, Competência e o Servidor.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

	_buildPaycheck: function(paycheck){

        var end_competence = this.getEndCompetenceField().getValue()
        var start_competence = this.getStartCompetenceField().getValue()
        engine.mq.Report.request({
            report: '/to/mpe/gfp/paycheck_by_id',
            waitMessage: 'Gerando relatório...',
            params: {

                outfile: 'contracheque'+'-' + start_competence + '-' + end_competence,
                report_name: 'Contra-cheque' + start_competence + '-' + end_competence,
                contracheque: paycheck,
                admin: 1
            }

        });
    },


    getEmployeeField: function (config) {
        if (!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Servidor',
                name: 'servidor',
                rest: 'rh.employee.Restful',
                allowBlank: true,
                lazyRender: true,
                lazyInit: true,
            });
        }
        
        return this._employeeField;
    },

    getStartCompetenceField: function(config){
        if(!this._start_competenceField)
            this._start_competenceField = Ext._create('Ext.form.TextField', {
                name: 'start_competence',
                fieldLabel: 'Competência Inicial (mm/aaaa)',
                width: 400,
            }, config);

        return this._start_competenceField;
    },


    getEndCompetenceField: function(config){
        if(!this._end_competenceField)
            this._end_competenceField = Ext._create('Ext.form.TextField', {
                name: 'end_competence',
                fieldLabel: 'Competência Final (mm/aaaa)',
                width: 400,
            }, config);

        return this._end_competenceField;
    },

	getMain: function(cfg){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    region: 'center',
		    height: 700,
            bodyStyle: {
                'background-color': `${this.BACKGROUND_COLOR}`,
            },           
            layout: {
                type: 'hbox',
                padding: `${this.GAP} ${this.GAP} ${this.BOTTOM_PADDING} ${this.LEFT_PADDING}`,
            },
            defaults: this._getDefaults(),
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	region: 'center',
                title: 'Impressão do Holerite',
                bwrapStyle: [
                    'border-radius: 0px 0 8px 8px;',
                    'background-color: #005a7c;',
                    'font-size: 14px;',
                    'font-weight: bold;',
                    'cursor: default;',
                    'user-select: none;',
                ].join(''),
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		name: 'fieldServidor',
	        		align: 'center',
	        		items:[
                        this.getStartCompetenceField(),
                        this.getEndCompetenceField(),
                        this.getEmployeeField(cfg),
                    {
                        xtype: 'button',
                        id: 'submit',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Holerite',
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
			   title: 'Relatório -> Holerite'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'fit',
				items:[ 
					this.getMain(cfg),
				]
			}
		);

		rh.reports.PayCheckManage.superclass.constructor.call(this, cfg);
	}
});