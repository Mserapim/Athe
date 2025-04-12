Ext._define('rh.gfp.reports.CedulaCAdminReport', {
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

    /**
    * Metodo que faz chamada Ajax para Download de Cédula-C
    */
	generateCedulaC: function(){
        if(this.getEmployeeField().getValue() && this.getYearField().getValue()){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'CedulaCIRPF',
                    'create_pdf_cedula_c'
                ),
                params: {
                    year: this.getYearField().getValue(),
                    employee: this.getEmployeeField().getValue(),
                    type: this.getTypeField().getValue()
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.success){
                        Ext.Msg.show({
                            title: 'Informe de Rendimentos',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                    }else
                        Ext.Msg.show({
                            title: 'Informe de Rendimentos',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                },
                failure: function(request) {
                    Ext.Msg.show({
                        title: 'Informe de Rendimentos',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                    });
                },
                scope: this
            });
        }else Ext.Msg.show({
            msg: 'Selecione o Servidor ou o ano.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
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
                title: 'Impressão do Informe de Rendimentos',
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
                        this.getYearField(cfg),
                        this.getEmployeeField(cfg),
                        this.getTypeField(cfg),
                    {
                        xtype: 'button',
                        id: 'submit',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Informe de Rendimentos',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this.generateCedulaC,
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

		rh.gfp.reports.CedulaCAdminReport.superclass.constructor.call(this, cfg);
	}
});
