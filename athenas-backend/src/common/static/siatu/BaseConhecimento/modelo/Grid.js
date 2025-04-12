/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.modelo.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.BaseConhecimento.modelo.Window',

    keywordFieldMessage: 'Descrição',

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Codigo', dataIndex: 'pk', width: 60, sortable:true},
                    {header: 'Descrição', dataIndex: 'descricao', id: 'autoExpandColumn', sortable:true},
                    {
                        header: 'Area', 
                        dataIndex: 'informatica', 
                        width: 100, 
                        hidden: true, 
                        sortable:true, 
                        renderer: function(value){ return value=='' ? 'Ambos' : value=='true' ? 'Informática' : 'Administrativo'}
                    },
                ]
            );

        return this._columnModel;
    },

    filterInformatica: function(checked, autoload) {
        autoload = core.nullValue(autoload, true);
        this.filtroInformatica = checked;
        this.setFilterProperty('informatica', this.filtroInformatica, 1000, autoload)
        data = new Date()
        data.setYear(data.getYear() + 1902)
        Ext.util.Cookies.set('siatu-area-informatica', Ext.encode(this.filtroInformatica), data);
    },

    getFilterMenu: function(cfg) {
        if (!this._filterMenu){
            this._filterMenu = [
                {
                    text: 'Área de Informática',
                    checked: this.filtroInformatica,
                    scope: this,
                    listeners: {
                        scope: this,
                        checkchange: function(btn, checked) {
                            this.filterInformatica(checked);
                        }
                    }
                }
            ]
        }
        return this._filterMenu
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg,{
            hideItemsToolbar: ['remove', 'download']
        })

        Ext.apply(cfg,{
            allowRemove: false,
            columnAction: false,
        })

        if (Ext.util.Cookies.get('siatu-area-informatica') != null)
            this.filtroInformatica = Ext.decode(Ext.util.Cookies.get('siatu-area-informatica'));
        else
            this.filtroInformatica = false;

        common.siatu.BaseConhecimento.modelo.Grid.superclass.constructor.call(this, cfg);
        this.getKeywordField().setWidth(230);
        this.setFilterProperty('informatica', this.filtroInformatica, 1000 , false)
        this.addFilterProperty('informatica', undefined, 1000 , false)
    }
    
})