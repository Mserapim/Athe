/**
 *
 **/

Ext._define('rh.reports.EmployeeLotation', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('ServidoresPorLotacaoRelatorio', 'generate_report'),
            params: {tipo: type},
            method: 'POST',
            success: function (request) {
                var obj = Ext.decode(request.responseText);
                if (obj.success){
                    Ext.Msg.show({
                        title: 'Solicitando Relatório',
                        msg: obj.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    if (obj.download){
                        var RemoteObserver = core.RemoteObserver;
                        var cb = RemoteObserver.on('base-report', {
                            scope: this,
                            fn: function (data) {
                                setTimeout(
                                    function() {
                                        toolkit.util.downloadFile({
                                            url: data.path,
                                            filename: data.filename,
                                            approach: 'download',
                                        });;
                                        RemoteObserver.un('base-report', {scope: this})
                                        setTimeout( function() {
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action(
                                                    'ServidoresPorLotacaoRelatorio',
                                                    'marker'
                                                ),
                                                params: {
                                                    uuid: obj.uuid
                                                },
                                                success: function() {},
                                                failure: function() {},
                                            });
                                        },
                                        2000);
                                    
                                    },
                                    1000
                                );
                            
                            }
                        });
                    }
                    
                }else{
                    Ext.Msg.show({
                        title: 'Error',
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }     
            },
            failure: function() {
                Ext.Msg.show({
                    msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                })
            },
            scope: this
        });	
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
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Lista de Servidores por Lotação',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        		{
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        menu: {
                            scope: this,
                            items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function (item) {
                                        this._buildReport(item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo DOCX',
                                    type: 'DOCX',
                                    iconCls: 'icon-ged icon-ged-application-msword',
                                    scope: this,
                                    handler: function (item) {
                                        this._buildReport(item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo XLSX',
                                    type: 'XLSX',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function (item) {
                                        this._buildReport(item.type);
                                    }
                                },
                            ]
                        },
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
			   title: 'Relatório -> Servidor por Lotação'
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

		rh.reports.EmployeeLotation.superclass.constructor.call(this, cfg);
	}
});