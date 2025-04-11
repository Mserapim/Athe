Ext._define('corregedoria.cirdir.AuditManage', {
    extend: 'toolkit.widget.TabPanel',
  
    getGrid: function(cfg) {
        if(!this._grid) {
            this._grid = Ext._create('corregedoria.cirdir.InformationEvaluationGrid', {
                region: 'center',
                // gridAutoLoad: true,
                height: Ext.getBody().getBox().height * 0.90,
                width: Ext.getBody().getBox().width * 0.55,
                detailView: this.getTilePanel(),
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });

            this._grid.setFilterProperty('checked', false, 100, true);
            
            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selected = sel.getSelected();
                    if(selected){
                        this.observer(selected.get('pk'));
                    } else {
                        this.observer();
                    }
                }
            });
        }
        return this._grid;
    },

    observer: function(value) {
        if(value) {
            this.readView(value);
        } else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },


    getBoxPanel: function(cfg) {
        if(!this._boxPanel)
            this._boxPanel = Ext._create('Ext.Panel', {
                region: 'center',
                split: true,
                border: false,
                autoHeight: true,
                items: [
                    this.getGrid(cfg),
                ]
            });
        return this._boxPanel;
    },
  
    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: Ext.getBody().getBox().width * 0.45,
                minWidth: Ext.getBody().getBox().width * 0.2, 
                maxWidth: Ext.getBody().getBox().width * 0.8
             });
        return this._tilePanel;
    },
  
    readView: function(pk) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = this.getGrid().factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document', pk),
            scope: this,
            autoAbort: true,
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    this.getTilePanel().setPageContent(rst.content);
                } else {
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },
   
    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        Ext.applyIf(
            cfg,
            {
                title: 'Auditoria SRDIR'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getBoxPanel(cfg),
                    this.getTilePanel(cfg)
                ],
            }
        );
        corregedoria.cirdir.AuditManage.superclass.constructor.call(this, cfg);
        this.observer();
    },
});
  