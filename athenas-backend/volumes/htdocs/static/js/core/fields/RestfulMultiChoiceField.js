
Ext._define('core.fields.RestfulMultiChoiceField', {
    extend: 'Ext.form.CompositeField',
    
    xtype: 'rest-multichoicefield',
    
    valueField: 'pk',
    
    setValue: function(value) {
        this._value = value;
        this.refreshValue();
    },
    
    refreshValue: function() {
        var select = this.getSelectBox().getEl();
        
        select.dom.innerHTML = '';
        this.getArrayValue().forEach(
            function(pk) {
                var option = document.createElement('option');
                option.value = pk;
                option.selected = true;
                option.innerHTML = '(' + pk + ')';
                
                select.appendChild(option);
            }
        );
    },
    
    getValue: function() { return this._value; },
    
    getArrayValue: function() {
        var value = this.getValue() || "";
        
        if(value === "")
            return [];
        else
            return value.split(',');
    },
     
    getValueField: function(cfg) {
        if(!this._valueField)
            this._valueField = Ext._create('Ext.form.Hidden', {});
    
        return this._valueField;
    },
    
    addItems: function(preSelected) {
        var selection = (preSelected || this.getAvailableGrid().getSelectionModel().getSelections());
        
        if(selection.length > 0) {
            var values = this.getArrayValue().concat(
                selection.map(function(data) { return data.get('pk') })
            );
            
            this.getAvailableGrid().setFilterProperty(
                this.valueField + '__in',
                values, 
                -100
            );
            
            this.getSelectedGrid().setFilterProperty(
                this.valueField + '__in',
                values, 
                100
            );
            
            var select = this.getSelectBox().getEl();
            
            this.setValue(values.join(','));
        } else {
            Ext.Msg.show({
                title: 'Adicionando itens',
                msg: 'Primeiro selecione os itens que deseja inserir.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },
    
    removeItems: function(preSelected) {
        var selection = (preSelected || this.getSelectedGrid().getSelectionModel().getSelections());
        
        if(selection.length > 0) {
            var selected = selection.map(function(data) { return data.get('pk') });
            var values = this.getArrayValue();
            
            selected.forEach(function(data) {
                values = values.filter(function(item) {
                    return item.toString() !== data.toString()
                })
            });
            
            this.getAvailableGrid().setFilterProperty(
                this.valueField + '__in',
                values, 
                -100
            );
            
            this.getSelectedGrid().setFilterProperty(
                this.valueField + '__in',
                values, 
                100
            );
            
            this.setValue(values.join(','));
        } else {
            Ext.Msg.show({
                title: 'Removendo itens',
                msg: 'Primeiro selecione os itens que deseja remover.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },
    
    getCommandPanel: function(cfg) {
        if(!this._commandPanel)
            this._commandPanel = Ext._create('Ext.Panel', {
                border: false,
                width: 60,
                layout: {
                    type: 'vbox',
                    align: 'center',
                    pack: 'center',
                },
                defaults: { 
                    xtype: 'button',
                    width: 32, 
                    height: 32
                },
                items: [
                    {
                        xtype: 'container',
                        bodyStyle: {
                            backgroundColor: 'red'
                        }
                    },
                    {
                        iconCls: 'icon-core icon-core-add-all',
                        scope: this,
                        handler: function() {
                            var preSelected = [];
                            
                            this.getAvailableGrid().getStore().each(
                                function(record) {
                                    preSelected.push(record);
                                }
                            )
                            
                            this.addItems(preSelected);
                        }
                    },
                    {
                        iconCls: 'icon-core icon-core-add-selected',
                        scope: this,
                        handler: function() { this.addItems(); }
                    },
                    {
                        iconCls: 'icon-core icon-core-remove-selected',
                        scope: this,
                        handler: function() { this.removeItems(); }
                    },
                    {
                        iconCls: 'icon-core icon-core-remove-all',
                        scope: this,
                        handler: function() {
                            var preSelected = [];
                            
                            this.getSelectedGrid().getStore().each(
                                function(record) {
                                    preSelected.push(record);
                                }
                            )
                            
                            this.removeItems(preSelected);
                        }
                    },
                ]
            });
    
        return this._commandPanel;
    },
    
    getAvailableGrid: function(cfg) {
        if(!this._availableGrid) {
            this._availableGrid = core.RestfulGrid.factoryGrid(cfg.restBase, {
                title: 'Disponíveis',
                flex: 1,
                gridAutoLoad: false,
                configOrderToolBar: ['search']
            });
            
            this._availableGrid.setFilterProperty(
                (cfg.valueField || this.valueField) + '__in',
                (cfg.value || []), 
                -100
            );
        }
    
        return this._availableGrid;
    },
    
    getSelectedGrid: function(cfg) {
        if(!this._selectedGrid) {
            this._selectedGrid = core.RestfulGrid.factoryGrid(cfg.restBase, {
                title: 'Selecionados',
                flex: 1,
                gridAutoLoad: false,
                configOrderToolBar: ['search']
            });
            
            this._selectedGrid.setFilterProperty(
                (cfg.valueField || this.valueField) + '__in',
                (cfg.value || []), 
                100
            );
        }
    
        return this._selectedGrid;
    },
    
    getSelectBox: function(cfg) {
        if(!this._selectBox)
            this._selectBox = Ext._create('Ext.Container', {
                autoEl: {
                    name: cfg.name,
                    tag: 'select',
                    multiple: true,
                    style: 'width: 100px; display: none'
                }
            });
    
        return this._selectBox;
    },
    
    constructor: function(cfg) {
        cfg = cfg || {};
        
        cfg.height = ((cfg.height || 0) < 450 ? 450 : cfg.height);
        
        Ext.apply(
            cfg,
            {
                items: [
                    {
                        xtype: 'container',
                        autoWidth: true,
                        autoHeight: true,
                        items: [
                            this.getSelectBox(cfg),
                            {
                                xtype: 'container',
                                height: cfg.height,
                                layout: {
                                    type: 'hbox',
                                    align: 'stretch'
                                },
                                items: [
                                    this.getAvailableGrid(cfg),
                                    this.getCommandPanel(cfg),
                                    this.getSelectedGrid(cfg),
                                ]
                            }
                        ]
                    }
                ]
            }
        );
        
        core.fields.RestfulMultiChoiceField.superclass.constructor.call(this, cfg);
    }
});

Ext.reg('rest-multichoicefield', core.fields.RestfulMultiChoiceField);