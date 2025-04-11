Ext._define('raf.nonproceduralactivities.Manage', {
  extend: 'toolkit.widget.TabPanel',

  getGrid: function() {
    if(!this._grid)
      this._grid = Ext._create('raf.nonproceduralactivities.Grid', {
        region: 'center',
        gridAutoLoad: false,
        configOrderToolBar: ['add', 'edit', 'remove', '-', 'search'],
      });
    return this._grid;
  },

  getToolbar: function(cfg) {
      if(!this._toolbar) {
          this._toolbar = Ext._create('Ext.Toolbar', {
              buttonAlign:'center',
              items: [
                  this.getChangeEmployeeAction()
              ]
          });
      }
      return this._toolbar;
  },

  openChangeWindow: function() {
      Ext._create('raf.functionalactivityreport.ChangeEmployeeWindow', {
          modal: true,
          callback: {
              success: {
                  scope: this,
                  fn: function(instance) {
                      this.employeeSelected(instance);
                  }
              }
          }
      }).show();
  },

  getChangeEmployeeAction: function() {
      if(!this._changeEmployeeAction){
          this._changeEmployeeAction = new Ext.Button({
              xtype: 'button',
              text: this.defaultText(),
              iconCls: 'icon-core icon-core-set-employee',
              scope: this,
              handler: function() {
                  this.openChangeWindow();
              }
          });
      }
      return this._changeEmployeeAction;
  },

  employeeSelected: function(instance) {
      if(instance) {
          this.getChangeEmployeeAction().setText(instance.data.pessoa_fisica_unicode);
          this.employee(instance.data.pk);
      } else if(!this.employee()){
          this.getChangeEmployeeAction().setText(this.defaultText());
          this.employee(null);
      }
  },

  defaultText: function() {
      return "Clique aqui para selecionar um Membro"
  },

  getChangeEmployeeAction: function() {
      if(!this._changeEmployeeAction){
          this._changeEmployeeAction = new Ext.Button({
              xtype: 'button',
              text: this.defaultText(),
              iconCls: 'icon-core icon-core-set-employee',
              scope: this,
              handler: function() {
                  this.openChangeWindow()
              }
          });
      }
      return this._changeEmployeeAction;
  },

  autoSelectionEmployee: function() {
      if(this.employee() === undefined) {
          var rest = Ext._create('raf.EmployeeRestful');
          var mask = new Ext.LoadMask(this.getEl(), {msg: 'Selecionando usuário...'});
          mask.show();
          rest.doRequest(
              rest.getRoute('employee_initial', false, 'GET', {
                  scope: this,
                  callback: function() {
                      mask.hide();
                      mask = null;
                  },
                  success: function(xhr) {
                      var rst = Ext.decode(xhr.responseText);
                      if(rst.success) {
                          this.employeeSelected(rst);
                      }
                      else
                          Ext.Msg.show({
                              title: 'Selecionando usuário',
                              icon: Ext.Msg.ERROR,
                              buttons: Ext.Msg.OK,
                              msg: rst.message
                          });
                  },
                  failure: function(xhr) {
                      Ext.Msg.show({
                          title: 'Selecionando usuário',
                          icon: Ext.Msg.ERROR,
                          buttons: Ext.Msg.OK,
                          msg: 'Nao foi possível realizar essa operação.'
                      });
                  }
              })
          );
      }
  },

  employee: function(value, dispatch) {
      dispatch = (dispatch === undefined ? true : dispatch);
      if(value !== undefined) {
          this._employee = value;

          if(dispatch) this.observerEmployee();
      }
      return this._employee;
  },

  observerEmployee: function() {
      var value = this.employee();
      if(value) {
          this.getGrid().setParam('member', value);
          this.getGrid().setFilterProperty('member', value, 1000);
      } else {
          this.getGrid().setParam('member', 0);
          this.getGrid().setFilterProperty('member', 0, 1000, false);
          this.getGrid().getStore().removeAll();
      }
  },

  constructor: function(cfg) {
      cfg = cfg ? cfg : {};
      Ext.applyIf(
          cfg,
          {
              title: 'Gestor de Atividades Não Procedimentais'
          }
      );
      Ext.apply(
          cfg,
          {
              layout: 'border',
              items: this.getGrid(),
              tbar: this.getToolbar(),
          }
      );
      raf.nonproceduralactivities.Manage.superclass.constructor.call(this, cfg);
      this.autoSelectionEmployee();
    },
});
